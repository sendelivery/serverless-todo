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

    def __init__(
        self,
        scope: Construct,
        id: str,
        prefix: str,
        ephemeral_deployment: bool = False,
        **kwargs,
    ) -> None:
        super().__init__(scope, id, **kwargs)

        # We'll create a VPC with the specified subnet configuration, the public subnets will be
        # used by our Fargate cluster, the isolated ones by our backend Lambdas and API Gateway.
        # 2 AZs is the minimum required for a LB to work with our Fargate cluster, so we'll stick
        # with that.
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

        # This is the security group we'll associate with our VPC interface endpoint.
        security_group = ec2.SecurityGroup(
            self,
            f"{prefix}VpcSecurityGroup",
            vpc=self._vpc,
            allow_all_outbound=True,
            security_group_name=f"{prefix}VpcSecurityGroup",
        )

        # Any resource deployed in one of the public subnets in our VPC will be able to send secure
        # traffic to our VPC interface endpoint.
        security_group.add_ingress_rule(
            ec2.Peer.any_ipv4(),
            ec2.Port.tcp(443),
            "Allow TCP from anywhere.",
        )

        if ephemeral_deployment:
            # Our VPC doesn't need an interface endpoint if we're in an ephemeral environment,
            # for simplicity, we'll expose our API GW endpoint to the open internet.
            self._vpc_interface_endpoint = None
        else:
            # This VPC interface endpoint will be used to secure our REST API and simulatneously
            # allow the web app that will be deployed in our public subnets to access the private
            # REST API.
            self._vpc_interface_endpoint = self._vpc.add_interface_endpoint(
                f"{prefix}VpcInterfaceEndpointForApi",
                service=ec2.InterfaceVpcEndpointAwsService.APIGATEWAY,
                subnets=ec2.SubnetSelection(
                    subnet_type=ec2.SubnetType.PRIVATE_ISOLATED
                ),
                security_groups=[security_group],
            )

        # This VPC gateway endpoint is required to allow the Lambdas housed in our private subnet
        # to access the DynamoDB table defined in our stateful stack.
        self._vpc.add_gateway_endpoint(
            f"{prefix}VpcGatewayEndpointForEntriesTable",
            service=ec2.GatewayVpcEndpointAwsService.DYNAMODB,
            subnets=[ec2.SubnetSelection(subnet_type=ec2.SubnetType.PRIVATE_ISOLATED)],
        )
