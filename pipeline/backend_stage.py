from constructs import Construct
from aws_cdk import RemovalPolicy, Stage

from backend.stateless.stateless_stack import StatelessStack
from backend.stateful.stateful_stack import StatefulStack


class ServerlessTodoBackendStage(Stage):
    @property
    def endpoint(self):
        return self._endpoint

    @property
    def api_key(self):
        return self._api_key

    def __init__(
        self,
        scope: Construct,
        id: str,
        prefix: str,
        stateful_removal_policy: RemovalPolicy = RemovalPolicy.RETAIN,
        **kwargs,
    ):
        super().__init__(scope, id, **kwargs)

        stateful = StatefulStack(
            self,
            f"{prefix}StatefulStack",
            prefix=prefix,
            removal_policy=stateful_removal_policy,
            **kwargs,
        )
        stateless = StatelessStack(
            self,
            f"{prefix}StatelessStack",
            prefix=prefix,
            entries_table=stateful.entries_table,
            **kwargs,
        )

        self._endpoint = stateless.endpoint
        self._api_key = stateless.api_key
