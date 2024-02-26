from aws_cdk import (
    Stack,
    aws_ec2 as ec2,
)
from constructs import Construct


class NetworkingStack(Stack):
    @property
    def vpc(self):
        """
        The VPC that will house all resources of our app.
        """
        return self._vpc

    @property
    def vpc_interface_endpoint(self):
        """
        VPC endpoint
        """
        return self._vpc_interface_endpoint

    def __init__(self, scope: Construct, id: str, prefix: str, **kwargs) -> None:
        super().__init__(scope, id, **kwargs)

        # TODO - outdated comment
        # We'll create a VPC with the default subnet configuration, the public subnets will be
        # used by our Fargate cluster, and the private ones by our backend Lambdas and API Gateway.
        # 2 AZs is the minimum required for a LB to work with our Fargate cluster, so we'll just
        # stick with that.
        self._vpc = ec2.Vpc(
            self,
            f"{prefix}Vpc",
            vpc_name=f"{prefix}Vpc",
            max_azs=2,
            subnet_configuration=[
                ec2.SubnetConfiguration(
                    name=f"{prefix}PrivateSubnet",
                    subnet_type=ec2.SubnetType.PRIVATE_ISOLATED,
                    cidr_mask=28,
                ),
                ec2.SubnetConfiguration(
                    name=f"{prefix}PublicSubnet",
                    subnet_type=ec2.SubnetType.PUBLIC,
                    cidr_mask=24,
                ),
            ],
        )

        security_group = ec2.SecurityGroup(
            self,
            f"{prefix}VpcSecurityGroup",
            vpc=self._vpc,
            allow_all_outbound=True,
            security_group_name=f"{prefix}VpcSecurityGroup",
        )

        security_group.add_ingress_rule(
            ec2.Peer.any_ipv4(),
            ec2.Port.tcp(443),
            "HTTPS from anywhere",
        )

        self._vpc_interface_endpoint = self._vpc.add_interface_endpoint(
            f"{prefix}VpcInterfaceEndpointForApi",
            service=ec2.InterfaceVpcEndpointAwsService.APIGATEWAY,
            subnets=ec2.SubnetSelection(subnet_type=ec2.SubnetType.PRIVATE_ISOLATED),
            security_groups=[security_group],
        )

        self._vpc.add_gateway_endpoint(
            f"{prefix}VpcGatewayEndpointForEntriesTable",
            service=ec2.GatewayVpcEndpointAwsService.DYNAMODB,
            subnets=[ec2.SubnetSelection(subnet_type=ec2.SubnetType.PRIVATE_ISOLATED)],
        )
