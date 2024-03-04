from constructs import Construct
from aws_cdk.aws_dynamodb import ITable
from aws_cdk.aws_ec2 import IVpc, IVpcEndpoint
from aws_cdk import (
    Stack,
    aws_ec2 as ec2,
    aws_lambda as _lambda,
    aws_apigateway as apigw,
    aws_iam as iam,
    aws_ssm as ssm,
)


# This stack consists of a handful of Lambdas for CRUD operations, each making use of a Lambda
# layer to interact with DynamoDB. They are fronted by a private API Gateway stage. The Lambdas
# are deployed to private subnets and access the REST API via a VPC interface endpoint.


class StatelessStack(Stack):
    @property
    def api(self):
        return self._api

    def __init__(
        self,
        scope: Construct,
        construct_id: str,
        prefix: str,
        entries_table: ITable,
        vpc: IVpc,
        vpc_endpoint: IVpcEndpoint,
        ephemeral_deployment: bool = False,
        **kwargs,
    ) -> None:
        super().__init__(scope, construct_id, **kwargs)

        # Resource policy for our private API, this will restrict our API so that it can only be
        # invoked via the designated VPC endpoint We don't configure this in ephemeral environments
        # for simplicity.
        if ephemeral_deployment:
            api_resource_policy = None
            endpoint_configuration = None
        else:
            api_resource_policy = iam.PolicyDocument(
                statements=[
                    iam.PolicyStatement(
                        effect=iam.Effect.ALLOW,
                        actions=["execute-api:Invoke"],
                        principals=[iam.AnyPrincipal()],
                        resources=["execute-api:/*/*/*"],
                    ),
                    iam.PolicyStatement(
                        effect=iam.Effect.DENY,
                        principals=[iam.AnyPrincipal()],
                        actions=["execute-api:Invoke"],
                        resources=["execute-api:/*/*/*"],
                        conditions={
                            "StringNotEquals": {
                                "aws:SourceVpce": vpc_endpoint.vpc_endpoint_id,
                            }
                        },
                    ),
                ]
            )

            endpoint_configuration = apigw.EndpointConfiguration(
                types=[apigw.EndpointType.PRIVATE],
                vpc_endpoints=[vpc_endpoint],
            )

        # Define the REST API - deploy "prod" by default
        self._api = apigw.RestApi(
            self,
            f"{prefix}ApiDeploymentStage",
            rest_api_name=f"{prefix}Api",
            deploy=True,
            policy=api_resource_policy,
            endpoint_configuration=endpoint_configuration,
        )
        entries_resource = self._api.root.add_resource("entries")

        # Next, we'll create Lambda integrations for our supported HTTP methods.

        # Define a Lambda layer for interacting with DynamoDB
        dynamo_lambda_layer = _lambda.LayerVersion(
            self,
            f"{prefix}DbUtils",
            layer_version_name=f"{prefix}DbUtils",
            code=_lambda.Code.from_asset("backend/stateless/lambda/layer"),
            description="Utility functions for interacting with our Todo entries database.",
            compatible_runtimes=[_lambda.Runtime.PYTHON_3_9],
        )

        # Define a Lambda function for the GET verb
        get_entries_function = _lambda.Function(
            self,
            f"{prefix}GetEntries",
            function_name=f"{prefix}GetEntries",
            runtime=_lambda.Runtime.PYTHON_3_9,
            handler="get_entries.handler",
            code=_lambda.Code.from_asset("backend/stateless/lambda/get_entries"),
            environment={"TABLE_NAME": entries_table.table_name},
            layers=[dynamo_lambda_layer],
            vpc=vpc,
            vpc_subnets=ec2.SubnetSelection(
                subnet_type=ec2.SubnetType.PRIVATE_ISOLATED
            ),
            log_format="JSON",
        )
        entries_table.grant(
            get_entries_function, "dynamodb:DescribeTable", "dynamodb:Scan"
        )

        # Define two Lambda functions for the POST / PUT and DELETE verbs respectively.
        upsert_entries_function = _lambda.Function(
            self,
            f"{prefix}UpsertEntries",
            function_name=f"{prefix}UpsertEntries",
            runtime=_lambda.Runtime.PYTHON_3_9,
            handler="upsert_entries.handler",
            code=_lambda.Code.from_asset("backend/stateless/lambda/upsert_entries"),
            environment={"TABLE_NAME": entries_table.table_name},
            layers=[dynamo_lambda_layer],
            vpc=vpc,
            vpc_subnets=ec2.SubnetSelection(
                subnet_type=ec2.SubnetType.PRIVATE_ISOLATED
            ),
            log_format="JSON",
        )
        entries_table.grant(
            upsert_entries_function,
            "dynamodb:DescribeTable",
            "dynamodb:PutItem",
            "dynamodb:UpdateItem",
        )

        delete_entries_function = _lambda.Function(
            self,
            f"{prefix}DeleteEntries",
            function_name=f"{prefix}DeleteEntries",
            runtime=_lambda.Runtime.PYTHON_3_9,
            handler="delete_entries.handler",
            code=_lambda.Code.from_asset("backend/stateless/lambda/delete_entries"),
            environment={"TABLE_NAME": entries_table.table_name},
            layers=[dynamo_lambda_layer],
            vpc=vpc,
            vpc_subnets=ec2.SubnetSelection(
                subnet_type=ec2.SubnetType.PRIVATE_ISOLATED
            ),
            log_format="JSON",
        )
        entries_table.grant(
            delete_entries_function, "dynamodb:DescribeTable", "dynamodb:DeleteItem"
        )

        # Lastly, we'll wire up the HTTP methods to their corresponding Lambdas.

        entries_resource.add_method(
            "GET",
            integration=apigw.LambdaIntegration(handler=get_entries_function),
        )

        entries_resource.add_method(
            "POST",
            integration=apigw.LambdaIntegration(handler=upsert_entries_function),
        )

        entries_resource.add_method(
            "PUT",
            integration=apigw.LambdaIntegration(handler=upsert_entries_function),
        )

        entries_resource.add_method(
            "DELETE",
            integration=apigw.LambdaIntegration(handler=delete_entries_function),
        )

        # We'll expose our API Gateway endpoint using SSM Parameter Store so we have an easy way of
        # accessing it later in our pipeline scripts.
        ssm.StringParameter(
            self,
            f"{prefix}ApiEndpoint",
            parameter_name=f"{prefix}ApiEndpoint",
            string_value=self._api.url,
        )
