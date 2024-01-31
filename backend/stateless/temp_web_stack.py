from aws_cdk import (
    Stack,
    aws_ecs as ecs,
    aws_ecs_patterns as ecs_patterns,
    aws_ec2 as ec2,
)
from constructs import Construct


# This is a temporary web stack... you should probably implement this as a construct instead of a stack
# and then import it into the stateless stack.
class FargateTest(Stack):
    def __init__(self, scope: Construct, construct_id: str, **kwargs) -> None:
        super().__init__(scope, construct_id, **kwargs)

        # Create VPC and Fargate Cluster
        # NOTE: Limit AZs to avoid reaching resource quotas
        vpc = ec2.Vpc(self, "MyVpc", max_azs=2)
        cluster = ecs.Cluster(self, "Ec2Cluster", vpc=vpc)

        ecs_patterns.ApplicationLoadBalancedFargateService(
            self,
            "Service",
            cluster=cluster,
            memory_limit_mib=1024,
            desired_count=1,
            cpu=512,
            task_image_options=ecs_patterns.ApplicationLoadBalancedTaskImageOptions(
                image=ecs.ContainerImage.from_registry("amazon/amazon-ecs-sample"),
                environment={
                    "TODO_API_ENDPOINT": "https://sbkra0myt3.execute-api.eu-west-2.amazonaws.com/prod/items",
                    "TODO_API_KEY": "J8PhcjHsmy3Pi91QZ96HM1NqzHmnXdHw6a8o46uv",
                },
            ),
            task_subnets=ec2.SubnetSelection(
                subnets=[
                    ec2.Subnet.from_subnet_id(
                        self, "subnet", "VpcISOLATEDSubnet1Subnet80F07FA0"
                    )
                ]
            ),
            load_balancer_name="application-lb-name",
        )
