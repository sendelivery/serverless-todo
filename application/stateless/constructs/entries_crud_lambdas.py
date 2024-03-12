from constructs import Construct
from aws_cdk.aws_dynamodb import ITable
from aws_cdk.aws_lambda import LayerVersion, Runtime, Function, Code
from aws_cdk.aws_ec2 import SubnetSelection, SubnetType, IVpc

from config import CommonConfig


class EntriesCrudLambdas(Construct):
    """This construct defines CRUD Lambdas that interact with our application's DynamoDB table
    created in the stateful stack.
    """

    @property
    def get_entries(self) -> Function:
        return self._get_entries

    @property
    def upsert_entry(self) -> Function:
        return self._upsert_entry

    @property
    def delete_entry(self) -> Function:
        return self._delete_entry

    def __init__(
        self,
        scope: Construct,
        id: str,
        entries_table: ITable,
        vpc: IVpc,
        config: CommonConfig,
    ) -> None:
        """Creates a set of CRUD Lambdas that interact with the entries table passed in.

        The defined Lambdas are exposed to the user as class properties for later use.
        - `get_entries`
        - `upsert_entry`
        - `delete_entry`

        Args:
            scope (Construct): The construct's parent or owner. This can either be a stack or
            another construct.
            id (str): The scoped ID of this construct.
            entries_table (ITable): The DynamoDB table our Lambda functions will interact with.
            vpc (IVpc): The VPC to deploy the Lambda functions in.
            config (CommonConfig): A user-defined configuration data class.
        """
        super().__init__(scope, id)

        prefix = config.prefix

        # Define a Lambda layer for interacting with DynamoDB
        dynamo_lambda_layer = LayerVersion(
            self,
            f"{prefix}DbUtils",
            layer_version_name=f"{prefix}DbUtils",
            code=Code.from_asset("application/stateless/lambda/layer"),
            description="Utility functions for interacting with our Todo entries database.",
            compatible_runtimes=[Runtime.PYTHON_3_9],
        )

        self._get_entries = Function(
            self,
            f"{prefix}GetEntries",
            function_name=f"{prefix}GetEntries",
            runtime=Runtime.PYTHON_3_9,
            handler="get_entries.handler",
            code=Code.from_asset("application/stateless/lambda/get_entries"),
            environment={"TABLE_NAME": entries_table.table_name},
            layers=[dynamo_lambda_layer],
            vpc=vpc,
            vpc_subnets=SubnetSelection(subnet_type=SubnetType.PRIVATE_ISOLATED),
            log_format="JSON",
            log_retention=config.log_retention,
        )
        entries_table.grant(
            self._get_entries, "dynamodb:DescribeTable", "dynamodb:Scan"
        )

        # This function will be used for both the POST and PUT verbs.
        self._upsert_entry = Function(
            self,
            f"{prefix}UpsertEntry",
            function_name=f"{prefix}UpsertEntry",
            runtime=Runtime.PYTHON_3_9,
            handler="upsert_entry.handler",
            code=Code.from_asset("application/stateless/lambda/upsert_entry"),
            environment={"TABLE_NAME": entries_table.table_name},
            layers=[dynamo_lambda_layer],
            vpc=vpc,
            vpc_subnets=SubnetSelection(subnet_type=SubnetType.PRIVATE_ISOLATED),
            log_format="JSON",
            log_retention=config.log_retention,
        )
        entries_table.grant(
            self._upsert_entry,
            "dynamodb:DescribeTable",
            "dynamodb:PutItem",
            "dynamodb:UpdateItem",
        )

        self._delete_entry = Function(
            self,
            f"{prefix}DeleteEntry",
            function_name=f"{prefix}DeleteEntry",
            runtime=Runtime.PYTHON_3_9,
            handler="delete_entry.handler",
            code=Code.from_asset("application/stateless/lambda/delete_entry"),
            environment={"TABLE_NAME": entries_table.table_name},
            layers=[dynamo_lambda_layer],
            vpc=vpc,
            vpc_subnets=SubnetSelection(subnet_type=SubnetType.PRIVATE_ISOLATED),
            log_format="JSON",
            log_retention=config.log_retention,
        )
        entries_table.grant(
            self._delete_entry, "dynamodb:DescribeTable", "dynamodb:DeleteItem"
        )
