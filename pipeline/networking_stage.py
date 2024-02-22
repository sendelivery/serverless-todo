from constructs import Construct
from aws_cdk import Stage

from backend.networking.networking_stack import NetworkingStack


class ServerlessTodoNetworkingStage(Stage):
    @property
    def vpc(self):
        return self._vpc

    def __init__(
        self,
        scope: Construct,
        id: str,
        prefix: str,
        **kwargs,
    ):
        super().__init__(scope, id, **kwargs)

        networking = NetworkingStack(self, f"{prefix}NetworkingStack", **kwargs)

        self._vpc = networking.vpc
