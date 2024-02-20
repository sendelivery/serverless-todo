from constructs import Construct
from aws_cdk import (
    Stack,
    pipelines as pipelines,
    aws_codedeploy as codedeploy,
)

from .lib.pipeline_role import PipelineRole
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
            role=PipelineRole(self, f"{prefix}PipelineRole").role,
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
                    "TodoFargateTaskDefinition "
                    f"{backend.endpoint.import_value}"
                ),
            ],
        )

        cd_application = codedeploy.EcsApplication.from_ecs_application_arn(
            self,
            id="cd_application_from_arn",
            ecs_application_arn="arn:aws:codedeploy:eu-west-2:460848972690:application:BlueGreenApplication",
        )
        cd_deployment_group = codedeploy.EcsDeploymentGroup.from_ecs_deployment_group_attributes(
            self,
            "ECSDeploymentGroupId",
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
                todo_endpoint=backend.endpoint.import_value,
                **kwargs,
            ),
            pre=[
                # This step uses the pipeline's source file set by default (i.e. GitHub),
                # meaning we don't have to copy the web directory in the pipeline's synth step
                # like we do the scripts directory.
                pipelines.ShellStep(
                    "BuildAndUploadDockerImage",
                    commands=[
                        "chmod a+x ./scripts/pipeline/push_to_ecr",
                        f"./scripts/pipeline/push_to_ecr {container_repository}",
                    ],
                )
            ],
            post=[configure_codedeploy_step, deploy_step],
        )
        ############################ WEB END ############################
