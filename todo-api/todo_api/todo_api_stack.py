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

        # Define a consumer Lambda function for our GET API
        get_items_function = _lambda.Function(self, "GetItems",
            runtime=_lambda.Runtime.PYTHON_3_9,
            handler="getItems.handler",
            code=_lambda.Code.from_asset("lambdas")
        )

        get_items_function.add_environment("TABLE_NAME", items_table.table_name)
        version = get_items_function.current_version

        # Grant our consumer Lambda permission to read from DynamoDB
        items_table.grant_read_data(get_items_function)

        # Define the REST API
        api = apigw.RestApi(self, "DeploymentStagesAPI",
            rest_api_name="todo-api",
            deploy=False
        )
        
        # Define GET method for /items
        items_resource = api.root.add_resource("items")
        items_get_method = items_resource.add_method("GET",
            authorization_type=apigw.AuthorizationType.IAM,
            integration=apigw.AwsIntegration(
                service="lambda",
                region=Aws.REGION,
                proxy=True,
                path=f"2015-03-31/functions/{get_items_function.function_arn}/invocations"
            )
        )

        # Define Dev resources
        dev_alias = _lambda.Alias(self, "DevAlias",
            alias_name="dev",
            version=version
        )

        dev_deployment = apigw.Deployment(self, "DevApiDeployment", api=api)
        dev_stage = apigw.Stage(self, "DevApiStage",
            deployment=dev_deployment,
            stage_name="dev",
            variables={
                "lambdaAlias": dev_alias.alias_name
            }
        )

        # Permission to invoke Dev Lambda
        dev_alias.add_permission("DevStageInvokeDevAliasPermission",
            principal=iam.ServicePrincipal("apigateway.amazonaws.com"),
            action="lambda:InvokeFunction",
            source_arn=api.arn_for_execute_api(
                method=items_get_method.http_method,
                path=items_resource.path,
                stage=dev_stage.stage_name
            )
        )

        # Define outputs
        CfnOutput(self, "ApiHostUrl",
            value=f"{api.rest_api_id}.execute-api.{Aws.REGION}.amazonaws.com",
            description="API Host URL"
        )