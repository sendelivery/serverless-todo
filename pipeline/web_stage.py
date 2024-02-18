from constructs import Construct
from aws_cdk import (
    Stage,
)
from backend.web.web_stack import WebStack


class ServerlessTodoWebStage(Stage):
    def __init__(
        self,
        scope: Construct,
        id: str,
        prefix: str,
        todo_endpoint: str,
        **kwargs,
    ):
        super().__init__(scope, id, **kwargs)

        WebStack(self, f"{prefix}WebStack", prefix, todo_endpoint)
