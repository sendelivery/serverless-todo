from aws_cdk import (
    Stack,
    aws_dynamodb as dynamo,
    aws_ecr as ecr,
    RemovalPolicy,
)
from constructs import Construct


# The stateful side of our application consists of a single DynamoDB table.


class StatefulStack(Stack):
    @property
    def entries_table(self):
        """
        The DynamoDB table used to store todo entries, created by our stateful stack.
        Using the table property will create an implicit CloudFormation output.
        """
        return self._entries_table

    @property
    def ecr_repository(self):
        return self._ecr_repository

    def __init__(
        self,
        scope: Construct,
        construct_id: str,
        prefix: str,
        removal_policy: RemovalPolicy = RemovalPolicy.RETAIN,
        **kwargs,
    ) -> None:
        super().__init__(scope, construct_id, **kwargs)

        # Define the DynamoDB table that will hold our todo entries
        self._entries_table = dynamo.Table(
            self,
            f"{prefix}EntriesTable",
            table_name=f"{prefix}EntriesTable",
            partition_key=dynamo.Attribute(name="Id", type=dynamo.AttributeType.STRING),
            removal_policy=removal_policy,
        )

        auto_delete_images = False
        lifecycle_rule = None
        if removal_policy == RemovalPolicy.DESTROY:
            auto_delete_images = True
            lifecycle_rule = [
                ecr.LifecycleRule(
                    description="Hold only 1 image in ephemeral repository.",
                    max_image_count=1,
                )
            ]

        repository_name = f"{prefix.lower()}web-container"

        self._ecr_repository = ecr.Repository(
            self,
            f"{prefix}ContainerRepo",
            repository_name=repository_name,
            auto_delete_images=auto_delete_images,
            lifecycle_rules=lifecycle_rule,
            removal_policy=removal_policy,
        )
