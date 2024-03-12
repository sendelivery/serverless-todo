from constructs import Construct
from aws_cdk import Stack, aws_dynamodb as dynamo, aws_ecr as ecr
from config import CommonConfig


class StatefulStack(Stack):
    """This stack defines the resources used for our application's persistent storage."""

    @property
    def entries_table(self):
        return self._entries_table

    @property
    def ecr_repository(self):
        return self._ecr_repository

    def __init__(
        self, scope: Construct, id: str, config: CommonConfig, **kwargs
    ) -> None:
        """This stack defines a DynamoDB table used to store application data and an ECR
        repository to store our web app's build image.

        Args:
            scope (Construct):This stack's parent or owner. This can either be a stack or another
            construct.
            id (str): The construct ID of this stack.
            config (CommonConfig): A user-defined configuration data class.
        """
        super().__init__(scope, id, **kwargs)

        prefix = config.prefix

        self._entries_table = dynamo.Table(
            self,
            f"{prefix}EntriesTable",
            table_name=f"{prefix}EntriesTable",
            partition_key=dynamo.Attribute(name="Id", type=dynamo.AttributeType.STRING),
            removal_policy=config.removal_policy,
        )

        self._ecr_repository = ecr.Repository(
            self,
            f"{prefix}ContainerRepo",
            repository_name=config.image_repository_name,
            auto_delete_images=config.auto_delete_images,
            lifecycle_rules=config.ecr_lifecycle_rule,
            removal_policy=config.removal_policy,
        )
