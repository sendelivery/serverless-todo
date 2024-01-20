from aws_cdk import (
    Stack,
    aws_dynamodb as dynamo,
)
from constructs import Construct


class StatefulStack(Stack):
    def __init__(self, scope: Construct, construct_id: str, **kwargs) -> None:
        super().__init__(scope, construct_id, **kwargs)

        # Define the DynamoDB table that will hold our todo entries
        self.entries_table = dynamo.Table(
            self,
            "ItemsTable",
            partition_key=dynamo.Attribute(name="Id", type=dynamo.AttributeType.STRING),
        )
