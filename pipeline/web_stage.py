from typing import Mapping
from constructs import Construct
from aws_cdk import (
    Stage,
    aws_ec2 as ec2,
)
from backend.web.web_stack import WebStack


class ServerlessTodoWebStage(Stage):
    def __init__(
        self,
        scope: Construct,
        id: str,
        prefix: str,
        # vpc: ec2.Vpc,
        # container_environment: Mapping[str, str],
        todo_endpoint: str,
        todo_endpoint_key: str,
        **kwargs,
    ):
        super().__init__(scope, id, **kwargs)

        WebStack(self, f"{prefix}WebStack", prefix, todo_endpoint, todo_endpoint_key)
