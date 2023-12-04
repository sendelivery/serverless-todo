from aws_cdk import (
    Stack,
    aws_lambda as _lambda,
    aws_apigateway as apigw,
    aws_iam as iam,
    Aws, CfnOutput
)
from constructs import Construct

class TodoApiStack(Stack):

    def __init__(self, scope: Construct, construct_id: str, **kwargs) -> None:
        super().__init__(scope, construct_id, **kwargs)

        # Define a Lambda function for our GET API
        get_items_function = _lambda.Function(self, "GetItems",
            runtime=_lambda.Runtime.PYTHON_3_9,
            handler="getItems.handler",
            code=_lambda.Code.from_asset("lambdas")
        )
        version = get_items_function.current_version

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
                path=f"2015-03-31/functions/{get_items_function.function_arn}:${{stageVariables.lambdaAlias}}/invocations"
            )
        )

        # Define Prod resources
        prod_alias = _lambda.Alias(self, "ProdGetItems",
            alias_name="prod",
            version=version
        )

        prod_deployment = apigw.Deployment(self, "ProdApiDeployment", api=api)
        prod_stage = apigw.Stage(self, "ProdApiStage",
            deployment=prod_deployment,
            stage_name="prod",
            variables={
                "lambdaAlias": prod_alias.alias_name
            }
        )

        # Permissions to invoke Prod Lambda
        prod_alias.add_permission("ProdStageInvokeProdAliasPermission",
            principal=iam.ServicePrincipal("apigateway.amazonaws.com"),
            action="lambda:InvokeFunction",
            source_arn=api.arn_for_execute_api(
                method=items_get_method.http_method,
                path=items_resource.path,
                stage=prod_stage.stage_name
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