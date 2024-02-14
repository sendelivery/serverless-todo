from constructs import Construct
from aws_cdk import (
    Stack,
    Stage,
    pipelines as pipelines,
)
from .networking_stage import ServerlessTodoNetworkingStage

from .backend_stage import ServerlessTodoBackendStage
from .lib.codebuild_execution_role import CodeBuildExecutionRole

from .web_stage import ServerlessTodoWebStage


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

        # networking = ServerlessTodoNetworkingStage(
        #     self, "TodoNetworkingStage", prefix="Todo", **kwargs
        # )
        # pipeline.add_stage(networking)

        backend = ServerlessTodoBackendStage(
            self, "TodoBackendStage", prefix="Todo", **kwargs
        )
        pipeline.add_stage(backend)

        container_repository = (
            "460848972690.dkr.ecr.eu-west-2.amazonaws.com/serverless-todo-web-app"
        )

        # container_environment = {
        #     "TODO_API_ENDPOINT": backend.endpoint,
        #     "TODO_API_KEY": backend.api_key,
        # }

        pipeline.add_stage(
            ServerlessTodoWebStage(
                self,
                "TempWebStage",
                prefix="Todo",
                # vpc=networking.vpc,
                # container_environment=container_environment,
                **kwargs,
            ),
            pre=[
                pipelines.CodeBuildStep(
                    "BuildAndUploadDockerImage",
                    role=CodeBuildExecutionRole(
                        self, "TodoCodeBuildExecutionRole"
                    ).role,
                    commands=[
                        "echo Setting environments variables...",
                        # 'TODO_API_ENDPOINT="$(aws ssm get-parameter --name TodoApiEndpoint --query Parameter.Value --output text)entries"',
                        # "export TODO_API_ENDPOINT",
                        # 'echo "$TODO_API_ENDPOINT"',
                        # 'TODO_API_KEY="$(aws ssm get-parameter --name TodoApiKey --query Parameter.Value --output text)"',
                        # "export TODO_API_KEY",
                        # 'echo "$TODO_API_KEY"',
                        "cd web/",
                        # 'echo TODO_API_ENDPOINT="$TODO_API_ENDPOINT" >> .env.local',
                        # 'echo TODO_API_KEY="$TODO_API_KEY" >> .env.local',
                        "echo Logging in to Amazon ECR...",
                        f"aws ecr get-login-password | docker login --username AWS --password-stdin {container_repository}",
                        "docker build -t todo-web-app .",
                        f"docker tag todo-web-app:latest {container_repository}:latest",
                        f"docker push {container_repository}:latest",
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
