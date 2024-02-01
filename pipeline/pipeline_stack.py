from constructs import Construct
from aws_cdk import (
    Stack,
    Stage,
    aws_iam as iam,
    pipelines as pipelines,
    # aws_codebuild as codebuild,
)
from .backend_stage import ServerlessTodoBackendStage
from backend.stateless.temp_web_stack import FargateTest


class ServerlessTodoPipelineStack(Stack):
    def __init__(self, scope: Construct, id: str, **kwargs) -> None:
        super().__init__(scope, id, **kwargs)

        # An IAM role to allow codebuild to push to an ECR repository
        role = iam.Role(
            self,
            "AllowUploadToEcrRepository",
            assumed_by=iam.ServicePrincipal("codepipeline.amazonaws.com"),
        )
        role.attach_inline_policy(
            iam.Policy(
                self,
                "blahblahID",
                document=iam.PolicyDocument(
                    statements=[
                        iam.PolicyStatement(
                            actions=[
                                "ecr:BatchCheckLayerAvailability",
                                "ecr:CompleteLayerUpload",
                                "ecr:GetAuthorizationToken",
                                "ecr:InitiateLayerUpload",
                                "ecr:PutImage",
                                "ecr:UploadLayerPart",
                            ],
                            resources=["*"],
                            effect=iam.Effect.ALLOW,
                        )
                    ]
                ),
            )
        )

        pipeline = pipelines.CodePipeline(
            self,
            "TodoPipeline",
            pipeline_name="TodoPipeline",
            role=role,
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

        deploy = ServerlessTodoBackendStage(
            self, "TodoBackendStage", prefix="Todo", **kwargs
        )
        pipeline.add_stage(deploy)

        pipeline.add_stage(
            TempWebStage(self, "TempWebStage", **kwargs),
            pre=[
                pipelines.CodeBuildStep(
                    "BuildAndUploadDockerImage",
                    commands=[
                        "cd web/",
                        "echo Logging in to Amazon ECR"
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
