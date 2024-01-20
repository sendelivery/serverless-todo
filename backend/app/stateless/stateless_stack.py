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


class StatelessStack(Stack):
    def __init__(
        self, scope: Construct, construct_id: str, entries_table: Table, **kwargs
    ) -> None:
        super().__init__(scope, construct_id, **kwargs)

        # Define a Lambda layer for interacting with DynamoDB
        dynamo_lambda_layer = _lambda.LayerVersion(
            self,
            "TodoDBUtils",
            code=_lambda.Code.from_asset("app/stateless/lambda/layer"),
            description="Utility functions for interacting with our Todo items database.",
            compatible_runtimes=[_lambda.Runtime.PYTHON_3_9],
        )

        # Define a consumer Lambda function for the GET verb
        get_items_function = _lambda.Function(
            self,
            "GetItems",
            runtime=_lambda.Runtime.PYTHON_3_9,
            handler="get_items.handler",
            code=_lambda.Code.from_asset("app/stateless/lambda/get_items"),
            environment={"TABLE_NAME": entries_table.table_name},
            layers=[dynamo_lambda_layer],
        )
        entries_table.grant(
            get_items_function, "dynamodb:DescribeTable", "dynamodb:Scan"
        )

        # Define producer Lambda functions for the POST / PUT and DELETE verbs
        upsert_item_function = _lambda.Function(
            self,
            "UpsertItem",
            runtime=_lambda.Runtime.PYTHON_3_9,
            handler="upsert_items.handler",
            code=_lambda.Code.from_asset("app/stateless/lambda/upsert_items"),
            environment={"TABLE_NAME": entries_table.table_name},
            layers=[dynamo_lambda_layer],
        )
        entries_table.grant(
            upsert_item_function,
            "dynamodb:DescribeTable",
            "dynamodb:PutItem",
            "dynamodb:UpdateItem",
        )
        delete_item_function = _lambda.Function(
            self,
            "DeleteItem",
            runtime=_lambda.Runtime.PYTHON_3_9,
            handler="delete_item.handler",
            code=_lambda.Code.from_asset("app/stateless/lambda/delete_item"),
            environment={"TABLE_NAME": entries_table.table_name},
            layers=[dynamo_lambda_layer],
        )
        entries_table.grant(
            delete_item_function, "dynamodb:DescribeTable", "dynamodb:DeleteItem"
        )

        # Define the REST API - deploy "latestDeployment" by default
        api = apigw.RestApi(
            self, "DeploymentStagesApi", rest_api_name="todo-api", deploy=True
        )
        items_resource = api.root.add_resource("items")

        # Let's create an API key and usage plan for our API stage
        # We don't need to worry about rate or burst limiting.
        key = api.add_api_key("TodoApiKey")
        plan = api.add_usage_plan("TodoApiUsagePlan", name="TodoUsagePlan")
        plan.add_api_key(key)

        # Associate the plan to our API stage
        plan.add_api_stage(stage=api.deployment_stage)

        # Define GET method for /items
        items_get_method = items_resource.add_method(
            "GET",
            authorization_type=None,
            api_key_required=True,
            integration=apigw.AwsIntegration(
                service="lambda",
                region=Aws.REGION,
                proxy=True,
                path=f"2015-03-31/functions/{get_items_function.function_arn}/invocations",
            ),
        )

        # Define POST method for /items
        items_post_method = items_resource.add_method(
            "POST",
            authorization_type=None,
            api_key_required=True,
            integration=apigw.AwsIntegration(
                service="lambda",
                region=Aws.REGION,
                proxy=True,
                path=f"2015-03-31/functions/{upsert_item_function.function_arn}/invocations",
            ),
        )

        # Define PUT method for /items
        items_put_method = items_resource.add_method(
            "PUT",
            authorization_type=None,
            api_key_required=True,
            integration=apigw.AwsIntegration(
                service="lambda",
                region=Aws.REGION,
                proxy=True,
                path=f"2015-03-31/functions/{upsert_item_function.function_arn}/invocations",
            ),
        )

        # Define DELETE method for /items
        items_delete_method = items_resource.add_method(
            "DELETE",
            authorization_type=None,
            api_key_required=True,
            integration=apigw.AwsIntegration(
                service="lambda",
                region=Aws.REGION,
                proxy=True,
                path=f"2015-03-31/functions/{delete_item_function.function_arn}/invocations",
            ),
        )

        # Permission to invoke the get_items Lambda from GET verb
        get_items_function.add_permission(
            "ApiGWInvokeGetItemsPermission",
            principal=iam.ServicePrincipal("apigateway.amazonaws.com"),
            action="lambda:InvokeFunction",
            source_arn=api.arn_for_execute_api(
                method=items_get_method.http_method, path=items_resource.path
            ),
        )

        # Permission to invoke the upsert_items Lambda from POST / PUT verbs
        upsert_item_function.add_permission(
            "ApiGWInvokeUpsertItemsPOSTPermission",
            principal=iam.ServicePrincipal("apigateway.amazonaws.com"),
            action="lambda:InvokeFunction",
            source_arn=api.arn_for_execute_api(
                method=items_post_method.http_method, path=items_resource.path
            ),
        )
        upsert_item_function.add_permission(
            "ApiGWInvokeUpsertItemsPUTPermission",
            principal=iam.ServicePrincipal("apigateway.amazonaws.com"),
            action="lambda:InvokeFunction",
            source_arn=api.arn_for_execute_api(
                method=items_put_method.http_method, path=items_resource.path
            ),
        )

        # Permission to invoke the delete_item Lambda from DELETE verb
        delete_item_function.add_permission(
            "ApiGWInvokeDeleteItemsPermission",
            principal=iam.ServicePrincipal("apigateway.amazonaws.com"),
            action="lambda:InvokeFunction",
            source_arn=api.arn_for_execute_api(
                method=items_delete_method.http_method, path=items_resource.path
            ),
        )

        # Define outputs
        CfnOutput(
            self,
            "TodoApiKeyArn",
            value=key.key_arn,
            description="Todo API Key ARN",
        )
