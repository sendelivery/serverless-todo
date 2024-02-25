from constructs import Construct
from aws_cdk import RemovalPolicy, Stage

from backend.networking.networking_stack import NetworkingStack
from backend.stateless.stateless_stack import StatelessStack
from backend.stateful.stateful_stack import StatefulStack


class ServerlessTodoBackendStage(Stage):
    def __init__(
        self,
        scope: Construct,
        id: str,
        prefix: str,
        stateful_removal_policy: RemovalPolicy = RemovalPolicy.RETAIN,
        **kwargs,
    ):
        super().__init__(scope, id, **kwargs)

        networking = NetworkingStack(
            self,
            f"{prefix}NetworkingStack",
            prefix=prefix,
            **kwargs,
        )

        stateful = StatefulStack(
            self,
            f"{prefix}StatefulStack",
            prefix=prefix,
            removal_policy=stateful_removal_policy,
            **kwargs,
        )

        StatelessStack(
            self,
            f"{prefix}StatelessStack",
            prefix=prefix,
            entries_table=stateful.entries_table,
            vpc=networking.vpc,
            vpc_endpoint=networking.vpc_endpoint,
            **kwargs,
        )
