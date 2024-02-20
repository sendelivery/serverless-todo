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
        input: pipelines.FileSet,
        deployment_group: codedeploy.IEcsDeploymentGroup,
    ):
        super().__init__("MyCodeDeployStep")

        self._input = input
        self._deployment_group = deployment_group

    def produce_action(
        self,
        stage: codepipeline.IStage,
        *,
        run_order,
        artifacts: pipelines.ArtifactMap,
    ):
        artifact = artifacts.to_code_pipeline(self._input)

        action = cp_actions.CodeDeployEcsDeployAction(
            action_name="CustomCodeDeployAction",
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
