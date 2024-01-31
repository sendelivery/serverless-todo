from constructs import Construct
from aws_cdk import (
    Stage,
    aws_sqs as sqs,
)


class ServerlessTodoBackendStage(Stage):
    def __init__(
        self,
        scope: Construct,
        id: str,
        **kwargs,
    ):
        super().__init__(scope, id, **kwargs)

        sqs.Queue(self, "TempQueue")
