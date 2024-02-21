from constructs import Construct
from aws_cdk import (
    Stack,
    pipelines as pipelines,
    aws_codedeploy as codedeploy,
    aws_iam as iam,
)

from .lib.bluegreen_deployment_step import BlueGreenDeploymentStep

from .backend_stage import ServerlessTodoBackendStage
from .web_stage import ServerlessTodoWebStage


class ServerlessTodoPipelineStack(Stack):
    def __init__(self, scope: Construct, id: str, prefix: str, **kwargs) -> None:
        super().__init__(scope, id, **kwargs)

        ############################ PIPELINE START ############################
        pipeline = pipelines.CodePipeline(
            self,
            f"{prefix}Pipeline",
            pipeline_name=f"{prefix}Pipeline",
            publish_assets_in_parallel=False,
            synth=pipelines.ShellStep(
                "Synth",
                input=pipelines.CodePipelineSource.git_hub(
                    "sendelivery/serverless-todo-app",
                    "feature/fargate-web-app",
                ),
                commands=[
                    "chmod a+x ./scripts/pipeline/synth",
                    "./scripts/pipeline/synth",
                ],
            ),
        )
        ############################ PIPELINE END ############################

        ############################ APPLICATION / STORAGE START ############################
        backend = ServerlessTodoBackendStage(
            self, f"{prefix}BackendStage", prefix=prefix, **kwargs
        )
        pipeline.add_stage(backend)
        ############################ APPLICATION / STORAGE END ############################

        ############################ WEB START ############################
        configure_codedeploy_step = pipelines.ShellStep(
            "ConfigureBlueGreenDeployment",
            input=pipeline.cloud_assembly_file_set,
            primary_output_directory="codedeploy",
            commands=[
                "ls",
                "chmod a+x ./codedeploy/configure_codedeploy_step",
                (
                    "./codedeploy/configure_codedeploy_step "
                    f"{self.account} "
                    f"{self.region} "
                    f"{'Todo'} "
                    f"{'Prod'} "
                    f"{pipeline.node.id} "
                    "TodoFargateTaskExecutionRole "
                    "TodoFargateTaskDefinition"
                ),
            ],
        )

        # To configure our Blue Green deployment step we'll need to give it a reference to the
        # deployment group created in our web stack. To do this, we'll first grab a reference to
        # the CodeDeploy application via its ARN.
        cd_application = codedeploy.EcsApplication.from_ecs_application_arn(
            self,
            id=f"{prefix}CodeDeployApplicationFromArn",
            ecs_application_arn=f"arn:aws:codedeploy:{self.region}:{self.account}:application:BlueGreenApplication",
        )

        # Next, we can grab the deployment group itself from the application.
        cd_deployment_group = codedeploy.EcsDeploymentGroup.from_ecs_deployment_group_attributes(
            self,
            f"{prefix}ECSDeploymentGroupId",
            application=cd_application,
            deployment_group_name="BlueGreenDeploymentGroup",
            deployment_config=codedeploy.EcsDeploymentConfig.CANARY_10_PERCENT_5_MINUTES,
        )

        deploy_step = BlueGreenDeploymentStep(
            input=configure_codedeploy_step.primary_output,
            deployment_group=cd_deployment_group,
        )
        deploy_step.add_step_dependency(configure_codedeploy_step)

        container_repository = (
            "460848972690.dkr.ecr.eu-west-2.amazonaws.com/serverless-todo-web-app"
        )

        pipeline.add_stage(
            ServerlessTodoWebStage(
                self,
                "TempWebStage",
                prefix="Todo",
                **kwargs,
            ),
            pre=[
                # This step uses the pipeline's source file set by default (i.e. GitHub),
                # meaning we don't have to copy the web directory in the pipeline's synth step
                # like we do the scripts directory.
                pipelines.CodeBuildStep(
                    "BuildAndUploadDockerImage",
                    commands=[
                        "chmod a+x ./scripts/pipeline/push_to_ecr",
                        f"./scripts/pipeline/push_to_ecr {container_repository}",
                    ],
                    role_policy_statements=[
                        iam.PolicyStatement(
                            actions=[
                                "ecr:BatchCheckLayerAvailability",
                                "ecr:CompleteLayerUpload",
                                "ecr:GetAuthorizationToken",
                                "ecr:InitiateLayerUpload",
                                "ecr:PutImage",
                                "ecr:UploadLayerPart",
                                "ecr:BatchGetImage",
                                "ecr:GetDownloadUrlForLayer",
                            ],
                            resources=["*"],
                            effect=iam.Effect.ALLOW,
                        )
                    ],
                )
            ],
            post=[configure_codedeploy_step, deploy_step],
        )
        ############################ WEB END ############################
