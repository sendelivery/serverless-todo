from constructs import Construct
from aws_cdk.aws_dynamodb import Table
from aws_cdk import (
    Stack,
    aws_lambda as _lambda,
    aws_apigateway as apigw,
    aws_iam as iam,
    Aws,
    CfnOutput,
)
from backend.stateless.lib.restapi_with_key import RestApiWithApiKey


# This stack consists of a handful of Lambdas for CRUD operations, each utilising the same layer
# to interact with DynamoDB. They are fronted by an API Gateway stage,


class StatelessStack(Stack):
    @property
    def endpoint(self):
        """
        The API Gateway endpoint of our backend application.
        """
        return self._endpoint

    def __init__(
        self, scope: Construct, construct_id: str, entries_table: Table, **kwargs
    ) -> None:
        super().__init__(scope, construct_id, **kwargs)

        # Define a Lambda layer for interacting with DynamoDB
        dynamo_lambda_layer = _lambda.LayerVersion(
            self,
            "TodoDbUtils",
            layer_version_name="TodoDbUtils",
            code=_lambda.Code.from_asset("backend/stateless/lambda/layer"),
            description="Utility functions for interacting with our Todo entries database.",
            compatible_runtimes=[_lambda.Runtime.PYTHON_3_9],
        )

        # Define a consumer Lambda function for the GET verb
        get_entries_function = _lambda.Function(
            self,
            "GetEntries",
            function_name="TodoGetEntries",
            runtime=_lambda.Runtime.PYTHON_3_9,
            handler="get_entries.handler",
            code=_lambda.Code.from_asset("backend/stateless/lambda/get_entries"),
            environment={"TABLE_NAME": entries_table.table_name},
            layers=[dynamo_lambda_layer],
        )
        entries_table.grant(
            get_entries_function, "dynamodb:DescribeTable", "dynamodb:Scan"
        )

        # Define producer Lambda functions for the POST / PUT and DELETE verbs
        upsert_entries_function = _lambda.Function(
            self,
            "UpsertEntries",
            function_name="TodoUpsertEntries",
            runtime=_lambda.Runtime.PYTHON_3_9,
            handler="upsert_entries.handler",
            code=_lambda.Code.from_asset("backend/stateless/lambda/upsert_entries"),
            environment={"TABLE_NAME": entries_table.table_name},
            layers=[dynamo_lambda_layer],
        )
        entries_table.grant(
            upsert_entries_function,
            "dynamodb:DescribeTable",
            "dynamodb:PutItem",
            "dynamodb:UpdateItem",
        )
        delete_entries_function = _lambda.Function(
            self,
            "DeleteItem",
            function_name="TodoDeleteEntries",
            runtime=_lambda.Runtime.PYTHON_3_9,
            handler="delete_entries.handler",
            code=_lambda.Code.from_asset("backend/stateless/lambda/delete_entries"),
            environment={"TABLE_NAME": entries_table.table_name},
            layers=[dynamo_lambda_layer],
        )
        entries_table.grant(
            delete_entries_function, "dynamodb:DescribeTable", "dynamodb:DeleteItem"
        )

        # Define a rest API with an API key using our custom construct
        api = RestApiWithApiKey(
            self, id="TodoApi", name="TodoApi", resource_name="entries"
        )
        self._endpoint = api.rest_api.url

        # Define GET method for /entries
        entries_get_method = api.resource.add_method(
            "GET",
            authorization_type=None,
            api_key_required=True,
            integration=apigw.AwsIntegration(
                service="lambda",
                region=Aws.REGION,
                proxy=True,
                path=f"2015-03-31/functions/{get_entries_function.function_arn}/invocations",
            ),
        )

        # Define POST method for /entries
        entries_post_method = api.resource.add_method(
            "POST",
            authorization_type=None,
            api_key_required=True,
            integration=apigw.AwsIntegration(
                service="lambda",
                region=Aws.REGION,
                proxy=True,
                path=f"2015-03-31/functions/{upsert_entries_function.function_arn}/invocations",
            ),
        )

        # Define PUT method for /entries
        entries_put_method = api.resource.add_method(
            "PUT",
            authorization_type=None,
            api_key_required=True,
            integration=apigw.AwsIntegration(
                service="lambda",
                region=Aws.REGION,
                proxy=True,
                path=f"2015-03-31/functions/{upsert_entries_function.function_arn}/invocations",
            ),
        )

        # Define DELETE method for /entries
        entries_delete_method = api.resource.add_method(
            "DELETE",
            authorization_type=None,
            api_key_required=True,
            integration=apigw.AwsIntegration(
                service="lambda",
                region=Aws.REGION,
                proxy=True,
                path=f"2015-03-31/functions/{delete_entries_function.function_arn}/invocations",
            ),
        )

        # Permission to invoke the get_entries Lambda from GET verb
        get_entries_function.add_permission(
            "ApiGWInvokeGetEntriesPermission",
            principal=iam.ServicePrincipal("apigateway.amazonaws.com"),
            action="lambda:InvokeFunction",
            source_arn=api.rest_api.arn_for_execute_api(
                method=entries_get_method.http_method, path=api.resource.path
            ),
        )

        # Permission to invoke the upsert_entries Lambda from POST / PUT verbs
        upsert_entries_function.add_permission(
            "ApiGWInvokeUpsertEntriesPOSTPermission",
            principal=iam.ServicePrincipal("apigateway.amazonaws.com"),
            action="lambda:InvokeFunction",
            source_arn=api.rest_api.arn_for_execute_api(
                method=entries_post_method.http_method, path=api.resource.path
            ),
        )
        upsert_entries_function.add_permission(
            "ApiGWInvokeUpsertEntriesPUTPermission",
            principal=iam.ServicePrincipal("apigateway.amazonaws.com"),
            action="lambda:InvokeFunction",
            source_arn=api.rest_api.arn_for_execute_api(
                method=entries_put_method.http_method, path=api.resource.path
            ),
        )

        # Permission to invoke the delete_entries Lambda from DELETE verb
        delete_entries_function.add_permission(
            "ApiGWInvokeDeleteEntriesPermission",
            principal=iam.ServicePrincipal("apigateway.amazonaws.com"),
            action="lambda:InvokeFunction",
            source_arn=api.rest_api.arn_for_execute_api(
                method=entries_delete_method.http_method, path=api.resource.path
            ),
        )

        # Define outputs
        CfnOutput(
            self,
            "TodoApiKeyArn",
            value=api.api_key.key_arn,
            description="Todo API Key ARN",
        )