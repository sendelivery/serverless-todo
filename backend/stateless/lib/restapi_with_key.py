from constructs import Construct
from aws_cdk.aws_apigateway import (
    RestApi,
    Resource,
    UsagePlan,
    IApiKey,
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

    @property
    def usage_plan(self) -> UsagePlan:
        return self._usage_plan

    @property
    def api_key(self) -> IApiKey:
        return self._api_key

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

        # Let's create an API key and usage plan for our API stage
        # We don't need to worry about rate or burst limiting.
        self._api_key = self._rest_api.add_api_key(
            f"{id}Key",
            api_key_name=f"{name}Key",
            # Consider setting the value of the API key with:
            # value=...
        )

        self._usage_plan = self._rest_api.add_usage_plan(
            f"{id}UsagePlan", name=f"{name}UsagePlan"
        )
        self._usage_plan.add_api_key(self._api_key)

        # Associate the plan to our API stage
        self._usage_plan.add_api_stage(stage=self._rest_api.deployment_stage)
