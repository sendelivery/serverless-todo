from constructs import Construct
from aws_cdk import (
    Stack,
    aws_codepipeline as codepipeline,
    aws_codepipeline_actions as cpactions,
    pipelines as pipelines,
    aws_codedeploy as codedeploy,
    aws_iam as iam,
)
import jsii

from .backend_stage import ServerlessTodoBackendStage
from .lib.codebuild_execution_role import CodeBuildExecutionRole
from .web_stage import ServerlessTodoWebStage


class ServerlessTodoPipelineStack(Stack):
    def __init__(self, scope: Construct, id: str, **kwargs) -> None:
        super().__init__(scope, id, **kwargs)

        ############################ PIPELINE START ############################
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
                    # TODO: "pytest tests"
                    "cdk synth",
                    # We need to include the codedeploy stuff in our pipeline's cloud assembly file set
                    "cp -r ./scripts/codedeploy cdk.out",
                ],
            ),
            publish_assets_in_parallel=False,
        )
        ############################ PIPELINE END ############################

        ############################ APPLICATION / STORAGE START ############################
        backend = ServerlessTodoBackendStage(
            self, "TodoBackendStage", prefix="Todo", **kwargs
        )
        pipeline.add_stage(backend)
        ############################ APPLICATION / STORAGE END ############################

        ############################ WEB START ############################
        container_repository = (
            "460848972690.dkr.ecr.eu-west-2.amazonaws.com/serverless-todo-web-app"
        )

        configure_codedeploy_step = pipelines.ShellStep(
            "ConfigureBlueGreenDeployment",
            input=pipeline.cloud_assembly_file_set,
            primary_output_directory="codedeploy",
            commands=[
                "ls",
                "chmod a+x ./codedeploy/codedeploy_configuration.sh",
                (
                    "./codedeploy/codedeploy_configuration.sh "
                    f"{self.account} "
                    f"{self.region} "
                    f"{'Todo'} "
                    f"{'Prod'} "
                    f"{pipeline.node.id} "
                    f"{'TODO-Service'}"
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

        deploy_step = CodeDeployStep(
            input=configure_codedeploy_step.primary_output,
            deployment_group=cd_deployment_group,
        )
        deploy_step.add_step_dependency(configure_codedeploy_step)

        pipeline.add_stage(
            ServerlessTodoWebStage(
                self,
                "TempWebStage",
                prefix="Todo",
                todo_endpoint=backend.endpoint.import_value,
                **kwargs,
            ),
            pre=[
                pipelines.CodeBuildStep(
                    "BuildAndUploadDockerImage",
                    role=CodeBuildExecutionRole(
                        self, "TodoCodeBuildExecutionRole"
                    ).role,
                    commands=[
                        "cd web/",
                        "echo Logging in to Amazon ECR...",
                        f"aws ecr get-login-password | docker login --username AWS --password-stdin {container_repository}",
                        "docker build -t todo-web-app .",
                        f"docker tag todo-web-app:latest {container_repository}:latest",
                        f"docker push {container_repository}:latest",
                    ],
                )
            ],
            post=[configure_codedeploy_step, deploy_step],
        )
        ############################ WEB END ############################


@jsii.implements(pipelines.ICodePipelineActionFactory)
class CodeDeployStep(pipelines.Step):
    def __init__(self, input: pipelines.FileSet, deployment_group):
        super().__init__("MyCodeDeployStep")

        self._input = input
        self._deployment_group = deployment_group

    def produce_action(
        self,
        stage: codepipeline.IStage,
        *,
        scope,
        action_name,
        run_order,
        artifacts: pipelines.ArtifactMap,
        pipeline,
    ):
        artifact = artifacts.to_code_pipeline(self._input)

        action = cpactions.CodeDeployEcsDeployAction(
            action_name="CustomCodeDeployAction",
            deployment_group=self._deployment_group,
            app_spec_template_input=artifact,
            task_definition_template_input=artifact,
            run_order=run_order,
            container_image_inputs=[
                cpactions.CodeDeployEcsContainerImageInput(
                    input=artifact,
                    task_definition_placeholder="IMAGE1_NAME",
                )
            ],
            variables_namespace="variable-namespace-",
        )

        stage.add_action(action)

        return pipelines.CodePipelineActionFactoryResult(run_orders_consumed=1)
