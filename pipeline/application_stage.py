from constructs import Construct
from aws_cdk import Stage, Stack
from application.networking import NetworkingStack
from application.stateless import StatelessStack
from application.stateful import StatefulStack
from application.web import WebStack
from config import CommonConfig


class ApplicationStage(Stage):
    """In CDK Pipelines, a Stage refers to a logical grouping of related stacks that are used to
    deploy copies of infrastructure stacks to different environments.

    This stage, is composed of all the application stacks required to deploy a copy of the
    Serverless Todo application infrastructure to any desired AWS environment (a region / account
    pair).
    """

    @property
    def networking_stack(self) -> Stack:
        return self._networking

    @property
    def stateful_stack(self) -> Stack:
        return self._stateful

    @property
    def stateless_stack(self) -> Stack:
        return self._stateless

    @property
    def web_stack(self) -> Stack:
        return self._web_stack

    def __init__(self, scope: Construct, id: str, config: CommonConfig, **kwargs):
        """In CDK Pipelines, a Stage refers to a logical grouping of related stacks that are used
        to deploy copies of infrastructure stacks to different environments.

        This stage, is composed of all the application stacks required to deploy a copy of the
        Serverless Todo application infrastructure to any desired AWS environment (a region /
        account pair).

        Args:
            scope (Construct):This stack's parent or owner. This can either be a stack or another
            construct.
            id (str): The construct ID of this stack.
            config (CommonConfig): A user-defined configuration data class.
        """
        super().__init__(scope, id, **kwargs)

        prefix = config.prefix

        self._networking = NetworkingStack(
            self, f"{prefix}NetworkingStack", config, **kwargs
        )

        self._stateful = StatefulStack(self, f"{prefix}StatefulStack", config, **kwargs)

        self._stateless = StatelessStack(
            self,
            f"{prefix}StatelessStack",
            self.stateful_stack.entries_table,
            self._networking.vpc,
            self._networking.vpc_interface_endpoint,
            config,
            **kwargs,
        )

        self._web_stack = WebStack(
            self,
            f"{prefix}WebStack",
            self._stateless.api,
            self._networking.vpc,
            self._stateful.ecr_repository,
            config,
            **kwargs,
        )
