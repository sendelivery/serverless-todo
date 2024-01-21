from constructs import Construct
from aws_cdk import (
    Stack,
    pipelines as pipelines,
)
from .pipeline_stage import ServerlessTodoPipelineStage


class ServerlessTodoPipelineStack(Stack):
    def __init__(self, scope: Construct, id: str, **kwargs) -> None:
        super().__init__(scope, id, **kwargs)

        # Pipeline code goes here
        pipeline = pipelines.CodePipeline(
            self,
            "ServerlessTodoPipeline",
            synth=pipelines.ShellStep(
                "Synth",
                input=pipelines.CodePipelineSource.git_hub(
                    "sendelivery/serverless-todo-app",
                    "chore/refactor-directory-for-cicd-pipeline",  # TODO: temporary, switch back to main
                ),
                commands=[
                    "npm install -g aws-cdk",
                    "pip install -r ./backend/requirements.txt",  # TODO: unsure about this step...
                    "cdk synth",
                ],
            ),
        )

        deploy = ServerlessTodoPipelineStage(
            self, "ServerlessTodoPipelineStage", **kwargs
        )
        deploy_stage = pipeline.add_stage(deploy)
