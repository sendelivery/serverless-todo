from constructs import Construct
from aws_cdk import Stage

from backend.stateless.stateless_stack import StatelessStack
from backend.stateful.stateful_stack import StatefulStack


class ServerlessTodoPipelineStage(Stage):
    @property
    def endpoint(self):
        return self._endpoint

    def __init__(self, scope: Construct, id: str, **kwargs):
        super().__init__(scope, id, **kwargs)

        stateful = StatefulStack(self, "ServerlessTodoStatefulStack", **kwargs)
        stateless = StatelessStack(
            self,
            "ServerlessTodoStatelessStack",
            entries_table=stateful.entries_table,
            **kwargs,
        )

        self._endpoint = stateless.endpoint
