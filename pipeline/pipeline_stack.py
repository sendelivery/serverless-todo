from constructs import Construct
from aws_cdk import (
    Stack,
    Stage,
    pipelines as pipelines,
    # aws_codebuild as codebuild,
)
from .backend_stage import ServerlessTodoBackendStage
from backend.stateless.temp_web_stack import FargateTest
from .lib.codebuild_execution_role import CodeBuildExecutionRole


class ServerlessTodoPipelineStack(Stack):
    def __init__(self, scope: Construct, id: str, **kwargs) -> None:
        super().__init__(scope, id, **kwargs)

        pipeline = pipelines.CodePipeline(
            self,
            "TodoPipeline",
            pipeline_name="TodoPipeline",
            # code_build_defaults=pipelines.CodeBuildOptions(
            # TODO: should I set the build environment here?
            #     build_environment=
            # )
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

        backend = ServerlessTodoBackendStage(
            self, "TodoBackendStage", prefix="Todo", **kwargs
        )
        pipeline.add_stage(backend)

        pipeline.add_stage(
            TempWebStage(self, "TempWebStage", **kwargs),
            pre=[
                pipelines.CodeBuildStep(
                    "BuildAndUploadDockerImage",
                    role=CodeBuildExecutionRole(
                        self, "TodoCodeBuildExecutionRole"
                    ).role,
                    commands=[
                        "echo Setting environments variables...",
                        'TODO_API_ENDPOINT="$(aws ssm get-parameter --name TodoApiEndpoint --query Parameter.Value --output text)entries"',
                        "export TODO_API_ENDPOINT",
                        'echo "$TODO_API_ENDPOINT"',
                        'TODO_API_KEY="$(aws ssm get-parameter --name TodoApiKey --query Parameter.Value --output text)"',
                        "export TODO_API_KEY",
                        'echo "$TODO_API_KEY"',
                        "cd web/",
                        "echo Logging in to Amazon ECR...",
                        "aws ecr get-login-password | docker login --username AWS --password-stdin 460848972690.dkr.ecr.eu-west-2.amazonaws.com",
                        "docker build -t test-todo .",
                        "docker tag serverless-todo-web-app:latest 460848972690.dkr.ecr.eu-west-2.amazonaws.com/serverless-todo-web-app:latest",
                        "docker push 460848972690.dkr.ecr.eu-west-2.amazonaws.com/serverless-todo-web-app:latest",
                    ],
                    # build_environment=codebuild.BuildEnvironment(
                    #     build_image=codebuild.LinuxBuildImage.STANDARD_7_0,
                    #     # privileged must be set to true only if this build project will be used to
                    #     # build Docker images, and the specified build environment image is not one
                    #     # provided by AWS CodeBuild with Docker support
                    #     privileged=True
                    # )
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
