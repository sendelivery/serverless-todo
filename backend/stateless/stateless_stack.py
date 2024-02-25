from constructs import Construct
from aws_cdk.aws_dynamodb import Table
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
# layer to interact with DynamoDB. They are fronted by an API Gateway stage.


class StatelessStack(Stack):
    def __init__(
        self,
        scope: Construct,
        construct_id: str,
        prefix: str,
        entries_table: Table,
        vpc: IVpc,
        vpc_endpoint: IVpcEndpoint,
        **kwargs,
    ) -> None:
        super().__init__(scope, construct_id, **kwargs)

        # Resource policy for our private API, this will restrict our API so that it can only be
        # invoked via the designated VPC endpoint.
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

        # Define the REST API - deploy "latestDeployment" by default
        api = apigw.RestApi(
            self,
            f"{prefix}ApiDeploymentStage",
            rest_api_name=f"{prefix}Api",
            deploy=True,
            endpoint_configuration=apigw.EndpointConfiguration(
                types=[apigw.EndpointType.PRIVATE],
                vpc_endpoints=[vpc_endpoint],
            ),
            policy=api_resource_policy,
        )
        entries_resource = api.root.add_resource("entries")

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
        )
        entries_table.grant(
            delete_entries_function, "dynamodb:DescribeTable", "dynamodb:DeleteItem"
        )

        # Lastly, we'll wire up the HTTP methods to their corresponding Lambdas.

        # Define GET method for /entries
        # TODO consider updating integration types to the LambdaIntegration class.
        entries_get_method = entries_resource.add_method(
            "GET",
            authorization_type=None,
            integration=apigw.AwsIntegration(
                service="lambda",
                proxy=True,
                path=f"2015-03-31/functions/{get_entries_function.function_arn}/invocations",
            ),
        )

        # Define POST method for /entries
        entries_post_method = entries_resource.add_method(
            "POST",
            authorization_type=None,
            integration=apigw.AwsIntegration(
                service="lambda",
                proxy=True,
                path=f"2015-03-31/functions/{upsert_entries_function.function_arn}/invocations",
            ),
        )

        # Define PUT method for /entries
        entries_put_method = entries_resource.add_method(
            "PUT",
            authorization_type=None,
            integration=apigw.AwsIntegration(
                service="lambda",
                proxy=True,
                path=f"2015-03-31/functions/{upsert_entries_function.function_arn}/invocations",
            ),
        )

        # Define DELETE method for /entries
        entries_delete_method = entries_resource.add_method(
            "DELETE",
            authorization_type=None,
            integration=apigw.AwsIntegration(
                service="lambda",
                proxy=True,
                path=f"2015-03-31/functions/{delete_entries_function.function_arn}/invocations",
            ),
        )

        # TODO - do we need these permissions??

        # Permission to invoke the get_entries Lambda from GET verb
        get_entries_function.add_permission(
            f"{prefix}ApiGWInvokeGetEntriesPermission",
            principal=iam.ServicePrincipal("apigateway.amazonaws.com"),
            action="lambda:InvokeFunction",
            source_arn=api.arn_for_execute_api(
                method=entries_get_method.http_method, path=entries_resource.path
            ),
        )

        # Permission to invoke the upsert_entries Lambda from POST / PUT verbs
        upsert_entries_function.add_permission(
            f"{prefix}ApiGWInvokeUpsertEntriesPOSTPermission",
            principal=iam.ServicePrincipal("apigateway.amazonaws.com"),
            action="lambda:InvokeFunction",
            source_arn=api.arn_for_execute_api(
                method=entries_post_method.http_method, path=entries_resource.path
            ),
        )
        upsert_entries_function.add_permission(
            f"{prefix}ApiGWInvokeUpsertEntriesPUTPermission",
            principal=iam.ServicePrincipal("apigateway.amazonaws.com"),
            action="lambda:InvokeFunction",
            source_arn=api.arn_for_execute_api(
                method=entries_put_method.http_method, path=entries_resource.path
            ),
        )

        # Permission to invoke the delete_entries Lambda from DELETE verb
        delete_entries_function.add_permission(
            f"{prefix}ApiGWInvokeDeleteEntriesPermission",
            principal=iam.ServicePrincipal("apigateway.amazonaws.com"),
            action="lambda:InvokeFunction",
            source_arn=api.arn_for_execute_api(
                method=entries_delete_method.http_method, path=entries_resource.path
            ),
        )

        # We'll expose our API Gateway endpoint using SSM Parameter Store so we have a decoupled
        # way of accessing it later in our pipeline and web stacks. Using a CfnOutput would make
        # it tricky to update the stateless stack in the event the API GW URL changed, as the
        # output would make this stack a dependant for the web stack, and thus cannot be updated!
        ssm.StringParameter(
            self,
            f"{prefix}ApiEndpoint",
            parameter_name=f"{prefix}ApiEndpoint",
            string_value=api.url,
        )
