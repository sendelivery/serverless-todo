from constructs import Construct
from aws_cdk import RemovalPolicy, Stage

from backend.networking import NetworkingStack
from backend.stateless import StatelessStack
from backend.stateful import StatefulStack
from backend.web import WebStack


class ApplicationStage(Stage):
    @property
    def stateful_stack(self):
        return self._stateful_stack

    @property
    def web_stack(self):
        return self._web_stack

    def __init__(
        self,
        scope: Construct,
        id: str,
        prefix: str,
        stateful_removal_policy: RemovalPolicy = RemovalPolicy.RETAIN,
        **kwargs,
    ):
        super().__init__(scope, id, **kwargs)

        # The networking stack defines the VPC, subnets, and VPC endpoints that will be used
        # throughout.
        networking = NetworkingStack(
            self,
            f"{prefix}NetworkingStack",
            prefix=prefix,
        )

        # The stateful stack defines our application's storage tier. In this case, just a DynamoDB
        # table.
        self._stateful_stack = StatefulStack(
            self,
            f"{prefix}StatefulStack",
            prefix=prefix,
            removal_policy=stateful_removal_policy,
            **kwargs,
        )

        # The stateless stack defines the application tier resources, CRUD Lambdas, and an API
        # Gateway REST API.
        self._stateless_stack = StatelessStack(
            self,
            f"{prefix}StatelessStack",
            prefix=prefix,
            entries_table=self.stateful_stack.entries_table,
            vpc=networking.vpc,
            vpc_endpoint=networking.vpc_interface_endpoint,
            **kwargs,
        )

        # The web stage defines the hosting solution for our Next.js web app. An ECS Fargate
        # cluster fronted by an ALB, we also create a target group used required for the deployment
        # strategy.
        self._web_stack = WebStack(
            self,
            f"{prefix}WebStack",
            prefix=prefix,
            api_endpoint=self._stateless_stack.api_endpoint,
            **kwargs,
        )
