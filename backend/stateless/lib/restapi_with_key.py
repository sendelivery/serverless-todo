from constructs import Construct
from aws_cdk.aws_apigateway import (
    RestApi,
    Resource,
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
