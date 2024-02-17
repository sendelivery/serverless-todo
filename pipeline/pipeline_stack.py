from typing import Any, Dict, Sequence
from aws_cdk.aws_codepipeline import (
    Artifact as _Artifact_0cb05964,
    IStage as _IStage_415fc571,
)
from constructs import Construct
from aws_cdk import (
    Environment,
    IPolicyValidationPluginBeta1,
    PermissionsBoundary,
    Stack,
    Stage,
    aws_codepipeline as codepipeline,
    aws_codepipeline_actions as codepipeline_actions,
    pipelines as pipelines,
    aws_codedeploy as codedeploy,
    aws_codebuild as codebuild,
    aws_ecs as ecs,
)
import jsii
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
            # use_change_sets=
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

        configure_codedeploy_step = pipelines.ShellStep(
            "ConfigureBlueGreenDeployment",
            input=pipeline.cloud_assembly_file_set,
            primary_output_directory="codedeploy",
            commands=[
                "chmod a+x ./pipeline/codedeploy/codedeploy_configuration.sh",
                f"./pipeline/codedeploy/codedeploy_configuration.sh {460848972690} {'eu-west-2'} {'Todo'} {'Prod'} {pipeline.node.id} {'TODO-Service'}",
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

        deploy_step = CodeDeployStep(
            "CodeDeployStep",
            file_set=configure_codedeploy_step.primary_output,
            deployment_group=cd_deployment_group,
            stage_name="CDStepStageName",
        )
        deploy_step.add_step_dependency(configure_codedeploy_step)

        pipeline.add_stage(
            ServerlessTodoWebStage(
                self,
                "TempWebStage",
                prefix="Todo",
                todo_endpoint=backend.endpoint.import_value,
                # todo_endpoint_key=backend.api_key.import_value,
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
            post=[configure_codedeploy_step, deploy_step],
        )


@jsii.implements(pipelines.ICodePipelineActionFactory)
class CodeDeployStep(pipelines.Step):
    def __init__(
        self,
        id: str,
        file_set: pipelines.FileSet,
        deployment_group: codedeploy.IEcsDeploymentGroup,
        stage_name: str,
    ) -> None:
        super().__init__(id)

        self._file_set = file_set
        self._deployment_group = deployment_group

        # codepipeline_actions.CodeDeployEcsDeployAction(
        #     action_name="Deploy",
        #     app_spec_template_input=
        # )

    def produce_action(
        self,
        stage: codepipeline.IStage,
        *,
        action_name: str,
        run_order: int,
        artifacts: pipelines.ArtifactMap,
    ) -> pipelines.CodePipelineActionFactoryResult:
        artifact = artifacts.to_code_pipeline(self._file_set)

        stage.add_action(
            action=codepipeline_actions.CodeDeployEcsDeployAction(
                action_name="DeployECS",
                app_spec_template_input=artifact,
                task_definition_template_input=artifact,
                run_order=run_order,
                container_image_inputs=[
                    codepipeline_actions.CodeDeployEcsContainerImageInput(
                        input=artifact,
                        task_definition_placeholder="Image1_Name",
                    )
                ],
                deployment_group=self._deployment_group,
                variables_namespace="deployment-prod-variables",
            )
        )

        return pipelines.CodePipelineActionFactoryResult(run_orders_consumed=1)

        # return super().produce_action(
        #     stage,
        #     action_name=action_name,
        #     artifacts=artifacts,
        #     pipeline=pipeline,
        #     run_order=run_order,
        #     scope=scope,
        #     stack_outputs_map=stack_outputs_map,
        #     before_self_mutation=before_self_mutation,
        #     code_build_defaults=code_build_defaults,
        #     fallback_artifact=fallback_artifact,
        #     variables_namespace=variables_namespace,
        # )
