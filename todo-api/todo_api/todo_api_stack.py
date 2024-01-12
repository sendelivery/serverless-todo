from aws_cdk import (
    Stack,
    aws_dynamodb as dynamo,
    aws_lambda as _lambda,
    aws_apigateway as apigw,
    aws_iam as iam,
    Aws,
    CfnOutput,
)
from constructs import Construct


class TodoApiStack(Stack):
    def __init__(self, scope: Construct, construct_id: str, **kwargs) -> None:
        super().__init__(scope, construct_id, **kwargs)

        # Define a DynamoDB table
        items_table = dynamo.Table(
            self,
            "ItemsTable",
            partition_key=dynamo.Attribute(name="Id", type=dynamo.AttributeType.STRING),
        )

        # Define a Lambda layer for interacting with DynamoDB
        dynamo_lambda_layer = _lambda.LayerVersion(
            self,
            "TodoDBUtils",
            code=_lambda.Code.from_asset("layer"),
            description="Utility functions for interacting with our Todo items database.",
            compatible_runtimes=[_lambda.Runtime.PYTHON_3_9],
        )

        # Define a consumer Lambda function for the GET verb
        get_items_function = _lambda.Function(
            self,
            "GetItems",
            runtime=_lambda.Runtime.PYTHON_3_9,
            handler="get_items.handler",
            code=_lambda.Code.from_asset("lambda/get_items"),
            environment={"TABLE_NAME": items_table.table_name},
            layers=[dynamo_lambda_layer],
        )
        items_table.grant(get_items_function, "dynamodb:DescribeTable", "dynamodb:Scan")

        # Define a producer Lambda function for the POST / PUT verbs
        upsert_items_function = _lambda.Function(
            self,
            "UpsertItems",
            runtime=_lambda.Runtime.PYTHON_3_9,
            handler="upsert_items.handler",
            code=_lambda.Code.from_asset("lambda/upsert_items"),
            environment={"TABLE_NAME": items_table.table_name},
            layers=[dynamo_lambda_layer],
        )
        items_table.grant(
            upsert_items_function,
            "dynamodb:DescribeTable",
            "dynamodb:PutItem",
            "dynamodb:UpdateItem",
        )

        # Define a Lambda function for the DELETE verb
        delete_item_function = _lambda.Function(
            self,
            "DeleteItems",
            runtime=_lambda.Runtime.PYTHON_3_9,
            handler="delete_item.handler",
            code=_lambda.Code.from_asset("lambda/delete_item"),
            environment={"TABLE_NAME": items_table.table_name},
            layers=[dynamo_lambda_layer],
        )
        items_table.grant(
            delete_item_function, "dynamodb:DescribeTable", "dynamodb:DeleteItem"
        )

        # Define the REST API - deploy "latestDeployment" by default
        api = apigw.RestApi(
            self, "DeploymentStagesAPI", rest_api_name="todo-api", deploy=True
        )
        items_resource = api.root.add_resource("items")

        # Define GET method for /items
        items_get_method = items_resource.add_method(
            "GET",
            authorization_type=apigw.AuthorizationType.IAM,
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
            authorization_type=apigw.AuthorizationType.IAM,
            integration=apigw.AwsIntegration(
                service="lambda",
                region=Aws.REGION,
                proxy=True,
                path=f"2015-03-31/functions/{upsert_items_function.function_arn}/invocations",
            ),
        )

        # Define PUT method for /items
        items_put_method = items_resource.add_method(
            "PUT",
            authorization_type=apigw.AuthorizationType.IAM,
            integration=apigw.AwsIntegration(
                service="lambda",
                region=Aws.REGION,
                proxy=True,
                path=f"2015-03-31/functions/{upsert_items_function.function_arn}/invocations",
            ),
        )

        # Define DELETE method for /items
        items_delete_method = items_resource.add_method(
            "DELETE",
            authorization_type=apigw.AuthorizationType.IAM,
            integration=apigw.AwsIntegration(
                service="lambda",
                region=Aws.REGION,
                proxy=True,
                path=f"2015-03-31/functions/{delete_item_function.function_arn}/invocations",
            ),
        )

        # Permission to invoke the get_items Lambda from GET verb
        get_items_function.add_permission(
            "APIGWInvokeGetItemsPermission",
            principal=iam.ServicePrincipal("apigateway.amazonaws.com"),
            action="lambda:InvokeFunction",
            source_arn=api.arn_for_execute_api(
                method=items_get_method.http_method, path=items_resource.path
            ),
        )

        # Permission to invoke the upsert_items Lambda from POST / PUT verbs
        upsert_items_function.add_permission(
            "APIGWInvokeUpsertItemsPOSTPermission",
            principal=iam.ServicePrincipal("apigateway.amazonaws.com"),
            action="lambda:InvokeFunction",
            source_arn=api.arn_for_execute_api(
                method=items_post_method.http_method, path=items_resource.path
            ),
        )
        upsert_items_function.add_permission(
            "APIGWInvokeUpsertItemsPUTPermission",
            principal=iam.ServicePrincipal("apigateway.amazonaws.com"),
            action="lambda:InvokeFunction",
            source_arn=api.arn_for_execute_api(
                method=items_put_method.http_method, path=items_resource.path
            ),
        )

        # Permission to invoke the delete_item Lambda from DELETE verb
        delete_item_function.add_permission(
            "APIGWInvokeDeleteItemsPermission",
            principal=iam.ServicePrincipal("apigateway.amazonaws.com"),
            action="lambda:InvokeFunction",
            source_arn=api.arn_for_execute_api(
                method=items_delete_method.http_method, path=items_resource.path
            ),
        )

        # Define outputs
        CfnOutput(
            self,
            "ApiHostUrl",
            value=f"{api.rest_api_id}.execute-api.{Aws.REGION}.amazonaws.com",
            description="API Host URL",
        )
