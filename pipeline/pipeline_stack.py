from constructs import Construct
from aws_cdk import (
    Stack,
    pipelines as pipelines,
)
from .pipeline_stage import ServerlessTodoPipelineStage


class ServerlessTodoPipelineStack(Stack):
    def __init__(self, scope: Construct, id: str, **kwargs) -> None:
        super().__init__(scope, id, **kwargs)

        pipeline = pipelines.CodePipeline(
            self,
            "TodoPipeline",
            pipeline_name="TodoPipeline",
            synth=pipelines.ShellStep(
                "Synth",
                input=pipelines.CodePipelineSource.git_hub(
                    "sendelivery/serverless-todo-app",
                    "main",
                ),
                commands=[
                    "npm install -g aws-cdk",
                    "pip install -r requirements.txt",
                    "cdk synth",
                    # TODO: "pytest tests"
                ],
            ),
        )

        deploy = ServerlessTodoPipelineStage(
            self, "TodoPipelineStage", prefix="Todo", **kwargs
        )
        pipeline.add_stage(deploy)
