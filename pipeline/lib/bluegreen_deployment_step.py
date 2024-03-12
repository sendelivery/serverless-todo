import jsii
from aws_cdk import (
    pipelines,
    aws_codepipeline as codepipeline,
    aws_codepipeline_actions as cp_actions,
    aws_codedeploy as codedeploy,
)


@jsii.implements(pipelines.ICodePipelineActionFactory)
class BlueGreenDeploymentStep(pipelines.Step):
    def __init__(
        self,
        input_fileset: pipelines.FileSet,
        deployment_group: codedeploy.IEcsDeploymentGroup,
        prefix: str,
    ):
        super().__init__(f"{prefix}BlueGreenDeploymentStep")

        self._input_fileset = input_fileset
        self._deployment_group = deployment_group
        self._prefix = prefix

    def produce_action(
        self,
        stage: codepipeline.IStage,
        *,
        run_order,
        artifacts: pipelines.ArtifactMap,
    ):
        artifact = artifacts.to_code_pipeline(self._input_fileset)

        action = cp_actions.CodeDeployEcsDeployAction(
            action_name=f"{self._prefix}CustomCodeDeployAction",
            deployment_group=self._deployment_group,
            app_spec_template_input=artifact,
            task_definition_template_input=artifact,
            run_order=run_order,
            container_image_inputs=[
                cp_actions.CodeDeployEcsContainerImageInput(
                    input=artifact,
                    task_definition_placeholder="IMAGE_PLACEHOLDER",
                )
            ],
        )

        stage.add_action(action)

        return pipelines.CodePipelineActionFactoryResult(run_orders_consumed=1)
