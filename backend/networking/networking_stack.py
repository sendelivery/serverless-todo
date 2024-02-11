from aws_cdk import (
    Stack,
    aws_ec2 as ec2,
)
from constructs import Construct


class NetworkingStack(Stack):
    @property
    def vpc(self):
        """
        The VPC that will house all applicable resources of our app.
        """
        return self._vpc

    def __init__(self, scope: Construct, id: str, **kwargs) -> None:
        super().__init__(scope, id, **kwargs)

        # We'll create a VPC with the default subnet configuration, the public subnets will be
        # used by our Fargate cluster, and the private ones by our backend Lambdas and API Gateway.
        # 2 AZs is the minimum required for a LB to work with our Fargate cluster, so we'll just
        # stick with that.
        self._vpc = ec2.Vpc(self, "TodoAppVpc", max_azs=2)
