from constructs import Construct
from aws_cdk import Stack, aws_ec2 as ec2
from config import CommonConfig


class NetworkingStack(Stack):
    """The networking stack defines the VPC, subnets, and VPC endpoints that will be used
    throughout."""

    @property
    def vpc(self):
        return self._vpc

    @property
    def vpc_interface_endpoint(self):
        return self._vpc_interface_endpoint

    def __init__(
        self,
        scope: Construct,
        id: str,
        config: CommonConfig,
        **kwargs,
    ) -> None:
        """This stack defines all the networking related resources to be used across our CDK app.

        If synthesised during an ephemeral deployment, a VPC interface endpoint for API Gateway
        will not be created.

        Args:
            scope (Construct):This stack's parent or owner. This can either be a stack or another
            construct.
            id (str): The construct ID of this stack.
            config (CommonConfig): A user-defined configuration data class.
        """
        super().__init__(scope, id, **kwargs)

        prefix = config.prefix

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

        if config.ephemeral:
            # We won't create an interface endpoint if we're in an ephemeral environment.
            # Our statelss resources can be exposed to the open internet for simplicity.
            self._vpc_interface_endpoint = None
        else:
            # This VPC interface endpoint will be used to secure our REST API and simultaneously
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
