from typing import Mapping
from aws_cdk import (
    Stack,
    CfnOutput,
    aws_ec2 as ec2,
    aws_ecs as ecs,
    aws_iam as iam,
    aws_ssm as ssm,
    aws_ecs_patterns as ecs_patterns,
)
from constructs import Construct


class WebStack(Stack):
    def __init__(
        self,
        scope: Construct,
        construct_id: str,
        prefix: str,
        # vpc: ec2.Vpc,
        # container_environment: Mapping[str, str],
        todo_endpoint: str,
        # todo_endpoint_key: str,
        **kwargs,
    ) -> None:
        super().__init__(scope, construct_id, **kwargs)

        # todo - figure out a solution to the 'dependency cannot cross stage boundaries' error
        vpc = ec2.Vpc(self, "TodoAppVpc", max_azs=2)

        cluster = ecs.Cluster(
            self,
            f"{prefix}FargateCluster",
            cluster_name=f"{prefix}FargateCluster",
            vpc=vpc,
        )

        task_role = iam.Role(
            self,
            f"{prefix}FargateTaskRole",
            assumed_by=iam.ServicePrincipal("ecs-tasks.amazonaws.com"),
        )

        execution_policy = iam.PolicyStatement(
            effect=iam.Effect.ALLOW,
            resources=["*"],
            actions=[
                "ecr:getauthorizationtoken",
                "ecr:batchchecklayeravailability",
                "ecr:getdownloadurlforlayer",
                "ecr:batchgetimage",
                "logs:createlogstream",
                "logs:putlogevents",
            ],
        )

        task_definition = ecs.FargateTaskDefinition(
            self, "ecs-taskdef", task_role=task_role, cpu=256, memory_limit_mib=512
        )
        task_definition.add_to_execution_role_policy(execution_policy)

        # Grab endpoint and key from SSM
        # TODO_API_ENDPOINT = ssm.StringParameter.value_for_string_parameter(
        #     self, parameter_name=f"{prefix}ApiEndpoint"
        # )
        # TODO_API_KEY = ssm.StringParameter.value_for_string_parameter(
        #     self, parameter_name=f"{prefix}ApiKey"
        # )
        # TODO_API_ENDPOINT = CfnOutput.import_value(f"{prefix}ApiEndpoint")
        # TODO_API_KEY = CfnOutput.import_value(f"{prefix}ApiKey")

        # Let's grab the latest build of our web app and use that in our task definition.
        base_image = "460848972690.dkr.ecr.eu-west-2.amazonaws.com/serverless-todo-web-app:latest"
        container = task_definition.add_container(
            "nextjs-fargate",
            image=ecs.ContainerImage.from_registry(base_image),
            environment={
                "TODO_API_ENDPOINT": todo_endpoint,
                # "TODO_API_KEY": todo_endpoint_key,
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
        )
