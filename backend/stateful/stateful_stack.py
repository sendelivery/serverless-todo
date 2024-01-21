from aws_cdk import (
    Stack,
    aws_dynamodb as dynamo,
)
from constructs import Construct


# The stateful side of our application consists of a single DynamoDB table. We can simply build the
# table within the stateful stack directly using an L2 construct.


class StatefulStack(Stack):
    @property
    def entries_table(self):
        """
        The DynamoDB table used to store todo entries, created by our stateful stack.
        """
        return self._entries_table

    def __init__(self, scope: Construct, construct_id: str, **kwargs) -> None:
        super().__init__(scope, construct_id, **kwargs)

        # Define the DynamoDB table that will hold our todo entries
        self._entries_table = dynamo.Table(
            self,
            "TodoEntriesTable",
            table_name="TodoEntriesTable",
            partition_key=dynamo.Attribute(name="Id", type=dynamo.AttributeType.STRING),
        )
