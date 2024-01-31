from constructs import Construct
from aws_cdk import (
    Stack,
    Stage,
    pipelines as pipelines,
)
from .backend_stage import ServerlessTodoBackendStage
from backend.stateless.temp_web_stack import FargateTest


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
                    "feature/fargate-web-app",
                ),
                commands=[
                    "npm install -g aws-cdk",
                    "pip install -r requirements.txt",
                    "cdk synth",
                    # TODO: "pytest tests"
                ],
            ),
            publish_assets_in_parallel=False,
        )

        deploy = ServerlessTodoBackendStage(
            self, "TodoBackendStage", prefix="Todo", **kwargs
        )
        pipeline.add_stage(deploy)

        pipeline.add_stage(
            TempWebStage(self, "TempWebStage", **kwargs),
            pre=[
                pipelines.CodeBuildStep(
                    "BuildAndUploadDockerImage",
                    commands=["cd web/", "docker build -t test-todo"],
                )
            ],
        )


class TempWebStage(Stage):
    def __init__(
        self,
        scope: Construct,
        id: str,
        **kwargs,
    ):
        super().__init__(scope, id, **kwargs)

        FargateTest(self, "FargateTest", **kwargs)
