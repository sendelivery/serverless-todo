from constructs import Construct
from aws_cdk import Stack
from aws_cdk.aws_apigateway import RestApi
from aws_cdk.aws_ec2 import IVpc, IVpcEndpoint
from aws_cdk.aws_dynamodb import ITable
from aws_cdk.aws_ssm import StringParameter
from .constructs import EntriesCrudLambdas, EntriesRestApi
from config import CommonConfig


class StatelessStack(Stack):
    """This stack defines a private API Gateway REST API and associated CRUD Lambda functions.

    If deploying in an ephemeral environment, the REST API is open to the public internet.
    """

    @property
    def api(self) -> RestApi:
        return self._api

    def __init__(
        self,
        scope: Construct,
        id: str,
        entries_table: ITable,
        vpc: IVpc,
        vpc_endpoint: IVpcEndpoint,
        config: CommonConfig,
        **kwargs,
    ) -> None:
        """This stack consists of a handful of Lambdas for CRUD operations, each making use of a
        Lambda layer to interact with the DynamoDB table passed in. They are fronted by a private
        API Gateway stage.

        The Lambdas are deployed to private subnets and access the REST API via a VPC interface
        endpoint.

        If deploying in an ephemeral environment, the REST API is open to the public internet.

        Args:
            scope (Construct):This stack's parent or owner. This can either be a stack or another
            construct.
            id (str): The construct ID of this stack.
            entries_table (ITable): The DynamoDB table defined in our stateful stack, the Lambda
            functions created in this stack will be assigned the appropriate IAM policies and
            interact with this table.
            vpc (IVpc): The VPC to deploy the Lambda functions in.
            vpc_endpoint (IVpcEndpoint): The VPC endpoint used to secure our API Gateway stage.
            config (CommonConfig): A user-defined configuration data class.
        """
        super().__init__(scope, id, **kwargs)

        prefix = config.prefix

        lambdas = EntriesCrudLambdas(
            self, f"{prefix}CrudLambdas", entries_table, vpc, config
        )

        rest_api = EntriesRestApi(
            self, f"{prefix}RestApi", lambdas, vpc_endpoint, config
        )
        self._api = rest_api.api

        # We'll expose our API Gateway endpoint using SSM Parameter Store so we have an easy way of
        # accessing it later in our pipeline scripts.
        StringParameter(
            self,
            f"{prefix}ApiEndpoint",
            parameter_name=f"{prefix}ApiEndpoint",
            string_value=self._api.url,
        )
