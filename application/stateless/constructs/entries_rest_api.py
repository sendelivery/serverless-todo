from constructs import Construct
from aws_cdk.aws_apigateway import (
    RestApi,
    EndpointConfiguration,
    EndpointType,
    LambdaIntegration,
)
from aws_cdk.aws_iam import PolicyDocument, PolicyStatement, Effect, AnyPrincipal
from aws_cdk.aws_ec2 import IVpcEndpoint
from .entries_crud_lambdas import EntriesCrudLambdas
from config import CommonConfig


class EntriesRestApi(Construct):
    """This construct defines a REST API fronting the CRUD Lambdas created in a separate
    construct.
    """

    @property
    def api(self) -> RestApi:
        return self._api

    def __init__(
        self,
        scope: Construct,
        id: str,
        lambdas: EntriesCrudLambdas,
        vpc_endpoint: IVpcEndpoint | None,
        config: CommonConfig,
    ) -> None:
        """This construct defines a REST that fronts the CRUD Lambdas created in a separate
        construct.

        If this construct is synthesised during an ephemeral deployment, the REST API will be
        created allowing traffic from the internet. Otherwise, the passed in VPC endpoint will be
        used to configure a private deployment of the REST API.

        Args:
            scope (Construct): The construct's parent or owner. This can either be a stack or
            another construct.
            id (str): The scoped ID of this construct.
            lambdas (EntriesCrudLambdas): An instance of the EntriesCrudLambdas construct that
            defines the Lambdas interacting with our application's database.
            vpc_endpoint (IVpcEndpoint | None): The VPC endpoint used to configure the private API.
            config (CommonConfig): A user-defined configuration data class.
        """
        super().__init__(scope, id)

        prefix = config.prefix

        # The resource policy for our private API, this will restrict our API so that it can only
        # be invoked via the designated VPC endpoint. We don't configure this in ephemeral
        # environments for simplicity - i.e. open to public access.
        if config.ephemeral:
            api_resource_policy = None
            endpoint_configuration = None
        else:
            api_resource_policy = PolicyDocument(
                statements=[
                    PolicyStatement(
                        effect=Effect.ALLOW,
                        actions=["execute-api:Invoke"],
                        principals=[AnyPrincipal()],
                        resources=["execute-api:/*/*/*"],
                    ),
                    PolicyStatement(
                        effect=Effect.DENY,
                        principals=[AnyPrincipal()],
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

            endpoint_configuration = EndpointConfiguration(
                types=[EndpointType.PRIVATE],
                vpc_endpoints=[vpc_endpoint],
            )

        # Define the REST API - deploy "prod" by default
        self._api = RestApi(
            self,
            f"{prefix}ApiDeploymentStage",
            rest_api_name=f"{prefix}Api",
            deploy=True,
            policy=api_resource_policy,
            endpoint_configuration=endpoint_configuration,
        )
        entries_resource = self._api.root.add_resource("entries")

        entries_resource.add_method(
            "GET", integration=LambdaIntegration(handler=lambdas.get_entries)
        )
        entries_resource.add_method(
            "POST", integration=LambdaIntegration(handler=lambdas.upsert_entry)
        )
        entries_resource.add_method(
            "PUT", integration=LambdaIntegration(handler=lambdas.upsert_entry)
        )
        entries_resource.add_method(
            "DELETE", integration=LambdaIntegration(handler=lambdas.delete_entry)
        )
