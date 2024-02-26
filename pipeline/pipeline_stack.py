from constructs import Construct
from aws_cdk import (
    Stack,
    pipelines as pipelines,
    aws_codedeploy as codedeploy,
    aws_iam as iam,
)

from .lib.bluegreen_deployment_step import BlueGreenDeploymentStep
from .application_stage import ApplicationStage


class ServerlessTodoPipelineStack(Stack):
    def __init__(self, scope: Construct, id: str, prefix: str, **kwargs) -> None:
        super().__init__(scope, id, **kwargs)

        pipeline = pipelines.CodePipeline(
            self,
            f"{prefix}Pipeline",
            pipeline_name=f"{prefix}Pipeline",
            publish_assets_in_parallel=False,
            synth=pipelines.ShellStep(
                "Synth",
                input=pipelines.CodePipelineSource.git_hub(
                    # TODO move these into environment variables
                    "sendelivery/serverless-todo",
                    "feature/private-resources",
                ),
                commands=[
                    "chmod a+x ./scripts/pipeline/synth",
                    "./scripts/pipeline/synth",
                ],
            ),
        )

        ############################ APPLICATION ############################

        application = ApplicationStage(
            self, f"{prefix}ApplicationStage", prefix=prefix, **kwargs
        )

        # TODO ECR repo should be created in the stateful stack.
        container_repository = f"{self.account}.dkr.ecr.{self.region}.amazonaws.com/serverless-todo-web-app"

        # This step uses the pipeline's source file set by default (i.e. GitHub),
        # meaning we don't have to copy the web directory in the pipeline's synth step
        # like we do the scripts directory.
        build_and_deploy_docker_image_step = pipelines.CodeBuildStep(
            f"{prefix}BuildAndUploadDockerImage",
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

        configure_codedeploy_step = pipelines.CodeBuildStep(
            "ConfigureBlueGreenDeployment",
            input=pipeline.cloud_assembly_file_set,
            primary_output_directory="codedeploy",
            role_policy_statements=[
                iam.PolicyStatement(
                    actions=["ssm:GetParameter"],
                    resources=[
                        f"arn:aws:ssm:{self.region}:{self.account}:parameter/{prefix}ApiEndpoint",
                    ],
                    effect=iam.Effect.ALLOW,
                )
            ],
            commands=[
                "ls",
                "chmod a+x ./codedeploy/configure_codedeploy_step",
                (
                    # View the script to view the details of the required parameters.
                    "./codedeploy/configure_codedeploy_step "
                    f"{pipeline.node.id} "
                    f"{self.account} "
                    f"{self.region} "
                    f"{prefix}Container "
                    f"{prefix}FargateTaskExecutionRole "
                    f"{prefix}FargateTaskDefinition "
                    f"{prefix}ApiEndpoint"
                ),
            ],
        )

        # To configure our Blue Green deployment step we'll need to give it a reference to the
        # deployment group created in our web stack. To do this, we'll first grab a reference to
        # the CodeDeploy application via its name, as opposed to ARN, since we're working in the
        # same environment.
        cd_application = codedeploy.EcsApplication.from_ecs_application_name(
            self,
            id=f"{prefix}CodeDeployApplicationFromName",
            ecs_application_name=f"{prefix}DeploymentApplication",
        )

        # Next, we can grab the deployment group itself from the application.
        cd_deployment_group = codedeploy.EcsDeploymentGroup.from_ecs_deployment_group_attributes(
            self,
            f"{prefix}ECSDeploymentGroupId",
            application=cd_application,
            deployment_group_name=f"{prefix}BlueGreenDeploymentGroup",
            deployment_config=codedeploy.EcsDeploymentConfig.CANARY_10_PERCENT_5_MINUTES,
        )

        deploy_step = BlueGreenDeploymentStep(
            input_fileset=configure_codedeploy_step.primary_output,
            deployment_group=cd_deployment_group,
            prefix=prefix,
        )

        # Deploying a "green" version of our application is dependent on having the correct task
        # definition and app spec files - i.e. the ouptput of our configure_codedeploy_step script.
        deploy_step.add_step_dependency(configure_codedeploy_step)

        pipeline.add_stage(
            application,
            stack_steps=[
                pipelines.StackSteps(
                    stack=application.web_stack,
                    # TODO change image step to pre step of stateless or post of stateful?
                    pre=[build_and_deploy_docker_image_step],
                    post=[configure_codedeploy_step, deploy_step],
                ),
            ],
        )

        ############################ APPLICATION ############################
