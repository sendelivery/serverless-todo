import secrets
import string
from constructs import Construct
from aws_cdk import RemovalPolicy
from aws_cdk.aws_apigateway import (
    RestApi,
    Resource,
    UsagePlan,
)


class RestApiWithApiKey(Construct):
    @property
    def rest_api(self) -> RestApi:
        return self._rest_api

    @property
    def resource(self) -> Resource:
        """
        The endpoint URI to which we can add HTTP methods to.

        e.g. `resource.add_method("GET" ...)`
        """
        return self._resource

    # @property
    # def usage_plan(self) -> UsagePlan:
    #     return self._usage_plan

    # @property
    # def api_key_value(self) -> str:
    #     return self._api_key_value

    def __init__(
        self, scope: Construct, id: str, name: str, resource_name: str, **kwargs
    ) -> None:
        super().__init__(scope, id, **kwargs)

        # Define the REST API - deploy "latestDeployment" by default
        self._rest_api = RestApi(
            self,
            f"{id}DeploymentStage",
            rest_api_name=name,
            deploy=True,
        )
        self._resource = self._rest_api.root.add_resource(resource_name)

        # todo - delete all the api key code, going forward we'll make our REST API a private one allows
        # invocations only to come from within our VPC.

        # # Let's create an API key and usage plan for our API stage

        # # First we'll generate an API key locally, this will only be used to allow our Dockerised
        # # web app to talk to our REST API. If we know the value ahead of time we can include it in
        # # our container's environment variables.

        # alphabet = string.ascii_letters + string.digits
        # while True:
        #     # Generate a 40 char alphanumeric string with at least one lowercase, one uppercase,
        #     # and three numeric characters.
        #     api_key_value = "".join(secrets.choice(alphabet) for i in range(40))
        #     if (
        #         any(c.islower() for c in api_key_value)
        #         and any(c.isupper() for c in api_key_value)
        #         and sum(c.isdigit() for c in api_key_value) >= 3
        #     ):
        #         break

        # self._api_key_value = api_key_value

        # # We don't need to worry about rate or burst limiting.
        # api_key = self._rest_api.add_api_key(
        #     f"{id}Key",
        #     api_key_name=f"{name}Key",
        #     value=api_key_value,
        # )
        # api_key.apply_removal_policy(RemovalPolicy.DESTROY)
        # api_key.

        # self._usage_plan = self._rest_api.add_usage_plan(
        #     f"{id}UsagePlan", name=f"{name}UsagePlan"
        # )
        # self._usage_plan.add_api_key(api_key)

        # # Associate the plan to our API stage
        # self._usage_plan.add_api_stage(stage=self._rest_api.deployment_stage)
