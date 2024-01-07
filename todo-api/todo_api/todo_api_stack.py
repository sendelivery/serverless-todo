from aws_cdk import (
    Stack,
    aws_dynamodb as dynamo,
    aws_lambda as _lambda,
    aws_apigateway as apigw,
    aws_iam as iam,
    Aws, CfnOutput
)
from constructs import Construct

class TodoApiStack(Stack):

    def __init__(self, scope: Construct, construct_id: str, **kwargs) -> None:
        super().__init__(scope, construct_id, **kwargs)

        # Define a DynamoDB table
        items_table = dynamo.Table(
            self, "ItemsTable",
            partition_key=dynamo.Attribute(
                name="user_id",
                type=dynamo.AttributeType.STRING
            ),
            sort_key=dynamo.Attribute(
                name="date_created",
                type=dynamo.AttributeType.STRING
            )
        )

        # Define a consumer Lambda function for the GET verb
        get_items_function = _lambda.Function(self, "GetItems",
            runtime=_lambda.Runtime.PYTHON_3_9,
            handler="get_items.handler",
            code=_lambda.Code.from_asset("lambda/get_items")
        )
        get_items_function.add_environment("TABLE_NAME", items_table.table_name)
        items_table.grant_read_data(get_items_function)

        # Define a producer Lambda function for the POST / PUT verbs
        upsert_items_function = _lambda.Function(self, "UpsertItems",
            runtime=_lambda.Runtime.PYTHON_3_9,
            handler="upsert_items.handler",
            code=_lambda.Code.from_asset("lambda/upsert_items")
        )
        upsert_items_function.add_environment("TABLE_NAME", items_table.table_name)
        items_table.grant_write_data(upsert_items_function)

        # Define the REST API - deploy "latestDeployment" by default
        api = apigw.RestApi(self, "DeploymentStagesAPI",
            rest_api_name="todo-api",
            deploy=True
        )
        items_resource = api.root.add_resource("items")

        # Define GET method for /items
        items_get_method = items_resource.add_method("GET",
            authorization_type=apigw.AuthorizationType.IAM,
            integration=apigw.AwsIntegration(
                service="lambda",
                region=Aws.REGION,
                proxy=True,
                path=f"2015-03-31/functions/{get_items_function.function_arn}/invocations"
            )
        )

        # Define POST method for /items
        items_post_method = items_resource.add_method("POST",
            authorization_type=apigw.AuthorizationType.IAM,
            integration=apigw.AwsIntegration(
                service="lambda",
                region=Aws.REGION,
                proxy=True,
                path=f"2015-03-31/functions/{upsert_items_function.function_arn}/invocations"
            )
        )
        
        # Define PUT method for /items
        items_put_method = items_resource.add_method("PUT",
            authorization_type=apigw.AuthorizationType.IAM,
            integration=apigw.AwsIntegration(
                service="lambda",
                region=Aws.REGION,
                proxy=True,
                path=f"2015-03-31/functions/{upsert_items_function.function_arn}/invocations"
            )
        )

        # Permission to invoke get_items Lambda
        get_items_function.add_permission("APIGWInvokeGetItemsPermission",
            principal=iam.ServicePrincipal("apigateway.amazonaws.com"),
            action="lambda:InvokeFunction",
            source_arn=api.arn_for_execute_api(
                method=items_get_method.http_method,
                path=items_resource.path,
            )
        )

        # Define outputs
        CfnOutput(self, "ApiHostUrl",
            value=f"{api.rest_api_id}.execute-api.{Aws.REGION}.amazonaws.com",
            description="API Host URL"
        )