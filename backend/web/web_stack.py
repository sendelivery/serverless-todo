from aws_cdk import (
    Duration,
    Stack,
    aws_ec2 as ec2,
    aws_ecs as ecs,
    aws_iam as iam,
    aws_ecs_patterns as ecs_patterns,
    aws_codedeploy as codedeploy,
    aws_elasticloadbalancingv2 as elb,
    aws_ssm as ssm,
)
from constructs import Construct


# This stack holds all the resources related to hosting our web app for public access. The solution
# consists of:
#   - A VPC with 2 AZs and an ECS Cluster wired up to that VPC.
#   - An ECS Fargate task definition and container that will be launched in our cluster.
#   - An L3 construct `ApplicationLoadBalancedFargateService` that provisions an ALB, handles
#     deploying our initial container with a desired count of 1, and routes traffic accordingly.
#
# We also provision a CodeDeploy application and deployment group, as well as a "green" LB target
# group. We'll use these in our production pipeline as part of the "Blue / Green" deployment
# strategy.


class WebStack(Stack):
    def __init__(
        self,
        scope: Construct,
        construct_id: str,
        prefix: str,
        **kwargs,
    ) -> None:
        super().__init__(scope, construct_id, **kwargs)

        # TODO move any networking related resources into a "networking" stack and expose resources
        # via CfnOutputs.
        vpc = ec2.Vpc(self, f"{prefix}Vpc", max_azs=2)

        cluster = ecs.Cluster(
            self,
            f"{prefix}Cluster",
            cluster_name=f"{prefix}Cluster",
            vpc=vpc,
        )

        task_role = iam.Role(
            self,
            f"{prefix}FargateTaskRole",
            role_name=f"{prefix}FargateTaskRole",
            assumed_by=iam.ServicePrincipal("ecs-tasks.amazonaws.com"),
            managed_policies=[
                iam.ManagedPolicy.from_aws_managed_policy_name(
                    "CloudWatchLogsFullAccess"
                )
            ],
        )

        # TODO pass this as a CF output, or find a deterministic way of getting in the custom code deploy step.
        # TODO narrow inline policy to the exact ECR repository we need.
        execution_role = iam.Role(
            self,
            f"{prefix}FargateTaskExecutionRole",
            role_name=f"{prefix}FargateTaskExecutionRole",
            assumed_by=iam.ServicePrincipal("ecs-tasks.amazonaws.com"),
            inline_policies={
                "AllowEcrCommands": iam.PolicyDocument(
                    statements=[
                        iam.PolicyStatement(
                            effect=iam.Effect.ALLOW,
                            resources=["*"],
                            actions=[
                                "ecr:GetAuthorizationToken",
                                "ecr:BatchCheckLayerAvailability",
                                "ecr:GetDownloadUrlForLayer",
                                "ecr:BatchGetImage",
                                "logs:CreateLogGroup",
                                "logs:CreateLogStream",
                                "logs:PutLogEvents",
                            ],
                        )
                    ]
                )
            },
        )

        # Create a task definition to tell ECS how to run our Next.js container.
        # Using defaults and the bare minimum in terms of CPU / RAM will be more than enough.
        task_definition = ecs.FargateTaskDefinition(
            self,
            f"{prefix}FargateTaskDefinition",
            family=f"{prefix}FargateTaskDefinition",
            task_role=task_role,
            execution_role=execution_role,
            cpu=256,
            memory_limit_mib=512,
        )

        # We'll add the container that will run the web app here, the container image will be the
        # one tagged as "latest" in our ECR repo. This alone, however, is not enough to handle
        # deploying new versions of our image. Hence the deployment group created further down.
        base_image = "460848972690.dkr.ecr.eu-west-2.amazonaws.com/serverless-todo-web-app:latest"

        # Source the API endpoint at deploy time, not synth time.
        todo_endpoint = ssm.StringParameter.value_for_string_parameter(
            self, f"{prefix}ApiEndpoint"
        )

        task_definition.add_container(
            f"{prefix}Container",
            container_name=f"{prefix}Container",
            image=ecs.ContainerImage.from_registry(base_image),
            environment={"TODO_API_ENDPOINT": todo_endpoint},
            memory_limit_mib=512,
            cpu=256,
            # https://stackoverflow.com/questions/55702196/essential-container-in-task-exited
            logging=ecs.AwsLogDriver(stream_prefix=prefix),
            port_mappings=[
                # Next.js uses port 3000 by default, we'll adhere to that.
                ecs.PortMapping(
                    host_port=3000, container_port=3000, protocol=ecs.Protocol.TCP
                )
            ],
        )

        # The ALB fronting our cluster will be internet-facing and be assigned a public IP so that
        # traffic can reach it via the public internet.
        # TODO does assign_public_ip need to be True?
        fargate_service = ecs_patterns.ApplicationLoadBalancedFargateService(
            self,
            f"{prefix}ALBFargateService",
            load_balancer_name=f"{prefix}Alb",
            service_name=f"{prefix}FargateService",
            cluster=cluster,
            task_definition=task_definition,
            desired_count=1,
            listener_port=80,
            assign_public_ip=True,
            public_load_balancer=True,
            deployment_controller=ecs.DeploymentController(
                type=ecs.DeploymentControllerType.CODE_DEPLOY
            ),
        )

        # From here on, we'll define the resources required for the Blue / Green deployment
        # strategy.

        # TODO how much of this is actually required by our deployment group?
        codedeploy_execution_role_policies = [
            iam.ManagedPolicy.from_aws_managed_policy_name("CloudWatchLogsFullAccess"),
            iam.ManagedPolicy.from_aws_managed_policy_name("AWSCodeDeployRoleForECS"),
            iam.ManagedPolicy.from_aws_managed_policy_name("AmazonECS_FullAccess"),
            iam.ManagedPolicy.from_aws_managed_policy_name(
                "AWSCodeBuildDeveloperAccess"
            ),
            iam.ManagedPolicy.from_aws_managed_policy_name(
                "AmazonEC2ContainerRegistryFullAccess"
            ),
            iam.ManagedPolicy.from_aws_managed_policy_name(
                "service-role/AWSLambdaBasicExecutionRole"
            ),
        ]

        codedeploy_execution_role = iam.Role(
            self,
            f"{prefix}BGDeploymentExecutionRole",
            role_name=f"{prefix}CodeDeployExecutionRole",
            assumed_by=iam.ServicePrincipal("codedeploy.amazonaws.com"),
            managed_policies=codedeploy_execution_role_policies,
        )

        app = codedeploy.EcsApplication(
            self,
            f"{prefix}BlueGreenApplication",
            application_name=f"{prefix}BlueGreenApplication",
        )

        green_target_group = elb.ApplicationTargetGroup(
            self,
            f"{prefix}GreenTargetGroup",
            target_group_name=f"{prefix}GreenTargetGroup",
            protocol=elb.ApplicationProtocol.HTTP,
            target_type=elb.TargetType.IP,
            vpc=vpc,
        )

        green_listener = fargate_service.load_balancer.add_listener(
            f"{prefix}GreenListener",
            port=8080,
            protocol=elb.ApplicationProtocol.HTTP,
            default_target_groups=[green_target_group],
        )

        codedeploy.EcsDeploymentGroup(
            self,
            f"{prefix}BlueGreenDeploymentGroupId",
            deployment_group_name=f"{prefix}BlueGreenDeploymentGroup",
            application=app,
            service=fargate_service.service,
            role=codedeploy_execution_role,
            blue_green_deployment_config=codedeploy.EcsBlueGreenDeploymentConfig(
                blue_target_group=fargate_service.target_group,
                green_target_group=green_target_group,
                listener=fargate_service.listener,
                test_listener=green_listener,
                deployment_approval_wait_time=Duration.minutes(10),
                termination_wait_time=Duration.minutes(5),
            ),
            deployment_config=codedeploy.EcsDeploymentConfig.CANARY_10_PERCENT_5_MINUTES,
        )
