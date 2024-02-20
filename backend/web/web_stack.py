from aws_cdk import (
    Duration,
    Stack,
    aws_ec2 as ec2,
    aws_ecs as ecs,
    aws_iam as iam,
    aws_ecs_patterns as ecs_patterns,
    aws_codedeploy as codedeploy,
    aws_elasticloadbalancingv2 as elb,
)
from constructs import Construct


class WebStack(Stack):
    def __init__(
        self,
        scope: Construct,
        construct_id: str,
        prefix: str,
        todo_endpoint: str,
        **kwargs,
    ) -> None:
        super().__init__(scope, construct_id, **kwargs)

        vpc = ec2.Vpc(self, f"{prefix}Vpc", max_azs=2)

        cluster = ecs.Cluster(
            self,
            f"{prefix}FargateCluster",
            cluster_name=f"{prefix}FargateCluster",
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
                                "ecr:getauthorizationtoken",
                                "ecr:batchchecklayeravailability",
                                "ecr:getdownloadurlforlayer",
                                "ecr:batchgetimage",
                                "logs:CreateLogGroup",
                                "logs:CreateLogStream",
                                "logs:PutLogEvents",
                            ],
                        )
                    ]
                )
            },
        )

        task_definition = ecs.FargateTaskDefinition(
            self,
            f"{prefix}FargateTaskDefinition",
            family=f"{prefix}FargateTaskDefinition",
            task_role=task_role,
            execution_role=execution_role,
            cpu=256,
            memory_limit_mib=512,
        )

        # Let's grab the latest build of our web app and use that in our task definition.
        base_image = "460848972690.dkr.ecr.eu-west-2.amazonaws.com/serverless-todo-web-app:latest"
        container = task_definition.add_container(
            f"{prefix}Container",
            image=ecs.ContainerImage.from_registry(base_image),
            environment={
                "TODO_API_ENDPOINT": todo_endpoint,
            },
            memory_limit_mib=256,
            cpu=256,
            # https://stackoverflow.com/questions/55702196/essential-container-in-task-exited
            logging=ecs.AwsLogDriver(stream_prefix=f"{prefix}-ecs-logs"),
        )
        container.add_port_mappings(
            ecs.PortMapping(
                host_port=3000, container_port=3000, protocol=ecs.Protocol.TCP
            )
        )

        fargate_service = ecs_patterns.ApplicationLoadBalancedFargateService(
            self,
            f"{prefix}ALBFargateService",
            cluster=cluster,
            task_definition=task_definition,
            public_load_balancer=True,
            desired_count=1,
            listener_port=80,
            assign_public_ip=True,
            deployment_controller=ecs.DeploymentController(
                type=ecs.DeploymentControllerType.CODE_DEPLOY
            ),
        )

        codedeploy_execution_role = iam.Role(
            self,
            "CodeDeployExecutionRoleId",
            assumed_by=iam.ServicePrincipal("codedeploy.amazonaws.com"),
            managed_policies=[
                iam.ManagedPolicy.from_aws_managed_policy_name(
                    "AWSCodeBuildDeveloperAccess"
                ),
                iam.ManagedPolicy.from_aws_managed_policy_name(
                    "AmazonEC2ContainerRegistryFullAccess"
                ),
                iam.ManagedPolicy.from_aws_managed_policy_name("AmazonECS_FullAccess"),
                iam.ManagedPolicy.from_aws_managed_policy_name(
                    "CloudWatchLogsFullAccess"
                ),
                iam.ManagedPolicy.from_aws_managed_policy_name(
                    "AWSCodeDeployRoleForECS"
                ),
                iam.ManagedPolicy.from_aws_managed_policy_name(
                    "service-role/AWSLambdaBasicExecutionRole"
                ),
            ],
        )

        app = codedeploy.EcsApplication(
            self, "BlueGreenApplicationId", application_name="BlueGreenApplication"
        )

        green_target_group = elb.ApplicationTargetGroup(
            self,
            "GreenTgId",
            protocol=elb.ApplicationProtocol.HTTP,
            target_group_name="GreenTgName",
            target_type=elb.TargetType.IP,
            vpc=vpc,
        )

        green_listener = fargate_service.load_balancer.add_listener(
            "GreenListener",
            port=8080,
            default_target_groups=[green_target_group],
            protocol=elb.ApplicationProtocol.HTTP,
        )

        green_listener.add_action(
            "GreenListenerActionId",
            action=elb.ListenerAction.forward(target_groups=[green_target_group]),
        )

        codedeploy.EcsDeploymentGroup(
            self,
            deployment_group_name="BlueGreenDeploymentGroup",
            id="BlueGreenDeploymentGroupId",
            application=app,
            service=fargate_service.service,
            role=codedeploy_execution_role,
            blue_green_deployment_config=codedeploy.EcsBlueGreenDeploymentConfig(
                blue_target_group=fargate_service.target_group,
                green_target_group=green_target_group,
                listener=fargate_service.listener,
                test_listener=green_listener,
                termination_wait_time=Duration.minutes(10),
                deployment_approval_wait_time=Duration.minutes(5),
            ),
            deployment_config=codedeploy.EcsDeploymentConfig.CANARY_10_PERCENT_5_MINUTES,
        )
