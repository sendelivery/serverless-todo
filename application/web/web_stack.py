from constructs import Construct
from aws_cdk.aws_apigateway import IRestApi
from aws_cdk.aws_ecr import IRepository
from aws_cdk.aws_ec2 import IVpc
from aws_cdk import (
    Stack,
    Duration,
    aws_ecs as ecs,
    aws_iam as iam,
    aws_ecs_patterns as ecs_patterns,
    aws_logs as logs,
)
from .constructs import BlueGreenEcsCodedeploy
from config import CommonConfig


class WebStack(Stack):
    """This stack defines the hosting solution for our Next.js web app."""

    def __init__(
        self,
        scope: Construct,
        id: str,
        api: IRestApi,
        vpc: IVpc,
        ecr_repo: IRepository,
        config: CommonConfig,
        **kwargs,
    ) -> None:
        """This stack holds all the resources related to hosting our web app for public access:
        - An ECS Fargate task definition and container that will be launched in a cluster.
        - An L3 construct `ApplicationLoadBalancedFargateService` that provisions an ALB, handles
        deploying our initial container with a desired count of 1, and routes traffic accordingly.

        If synthesising via the CICD pipeline, we also providion CodeDeploy resources necessary for
        a blue / green deployment of our ECS application.

        Args:
            scope (Construct): This stack's parent or owner. This can either be a stack or another
            construct.
            id (str): The construct ID of this stack.
            api (IRestApi): The REST API defined by the stateless stack.
            vpc (IVpc): The VPC created in the networking stack.
            ecr_repo (IRepository): The ECR repository created in the stateful stack.
            config (CommonConfig): A user-defined configuration data class.
        """
        super().__init__(scope, id, **kwargs)

        prefix = config.prefix

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
                                "logs:CreateLogGroup",
                                "logs:CreateLogStream",
                                "logs:PutLogEvents",
                            ],
                        )
                    ]
                )
            },
        )
        ecr_repo.grant_pull(execution_role)

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

        log_group = logs.LogGroup(
            self,
            f"{prefix}WebContainersLogGroup",
            log_group_name=f"{prefix}WebContainers",
            retention=logs.RetentionDays.ONE_WEEK,
            removal_policy=config.removal_policy,
        )

        task_definition.add_container(
            f"{prefix}Container",
            container_name=f"{prefix}Container",
            image=ecs.ContainerImage.from_registry(
                ecr_repo.repository_uri_for_tag("latest")
            ),
            environment={"TODO_API_ENDPOINT": api.url},
            memory_limit_mib=512,
            cpu=256,
            logging=ecs.AwsLogDriver(stream_prefix=prefix, log_group=log_group),
            port_mappings=[
                # Next.js uses port 3000 by default, we'll adhere to that.
                ecs.PortMapping(
                    host_port=3000, container_port=3000, protocol=ecs.Protocol.TCP
                )
            ],
        )

        # The ALB fronting our cluster will be internet-facing and be assigned a public IP so that
        # traffic from the open internet can reach it.
        fargate_service = ecs_patterns.ApplicationLoadBalancedFargateService(
            self,
            f"{prefix}ALBFargateService",
            load_balancer_name=f"{prefix}Alb",
            service_name=f"{prefix}FargateService",
            cluster=cluster,  # VPC is taken from the cluster
            task_definition=task_definition,
            desired_count=1,
            listener_port=80,
            assign_public_ip=True,  # places our containers in our VPC's public subnets by default
            public_load_balancer=True,
            deployment_controller=ecs.DeploymentController(
                type=config.web_deployment_controller_type
            ),
        )

        fargate_service.target_group.configure_health_check(
            healthy_http_codes="200",
            path="/health",
            interval=Duration.minutes(5),
        )

        # When deploying ephemeral stacks, we don't need to spin up any CodeDeploy resources. Those
        # are only used by our CICD pipeline, thus not necessary.
        if config.ephemeral:
            return

        BlueGreenEcsCodedeploy(
            self, f"{prefix}BlueGreenEcsCodedeploy", fargate_service, vpc, config
        )
