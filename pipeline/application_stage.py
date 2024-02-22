from constructs import Construct
from aws_cdk import RemovalPolicy, Stage

from backend.stateless.stateless_stack import StatelessStack
from backend.stateful.stateful_stack import StatefulStack
from backend.web.web_stack import WebStack


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

        # The stateful stack defines our application's storage tier. In this case, just a DynamoDB
        # table.
        stateful = StatefulStack(
            self,
            f"{prefix}StatefulStack",
            prefix=prefix,
            removal_policy=stateful_removal_policy,
            **kwargs,
        )

        # The stateless stack defines the application tier resources, CRUD Lambdas, and an API
        # Gateway REST API.
        stateless = StatelessStack(
            self,
            f"{prefix}StatelessStack",
            prefix=prefix,
            entries_table=stateful.entries_table,
            **kwargs,
        )

        # The web stage defines the hosting solution for our Next.js web app. An ECS Fargate
        # cluster fronted by an ALB, we also create a target group used required for the deployment
        # strategy.
        WebStack(
            self,
            f"{prefix}WebStack",
            prefix=prefix,
            todo_endpoint=stateless.endpoint,
            **kwargs,
        )
