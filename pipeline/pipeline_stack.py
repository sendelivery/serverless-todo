from constructs import Construct
from aws_cdk import (
    Stack,
    pipelines as pipelines,
    aws_codedeploy as codedeploy,
    aws_iam as iam,
)
from .lib.bluegreen_deployment_step import BlueGreenDeploymentStep
from .application_stage import ApplicationStage
from config import CommonConfig


class PipelineStack(Stack):
    def __init__(
        self,
        scope: Construct,
        id: str,
        config: CommonConfig,
        **kwargs,
    ) -> None:
        super().__init__(scope, id, **kwargs)

        prefix = config.prefix

        pipeline = pipelines.CodePipeline(
            self,
            f"{prefix}Pipeline",
            pipeline_name=f"{prefix}Pipeline",
            publish_assets_in_parallel=False,
            synth=pipelines.ShellStep(
                "Synth",
                input=pipelines.CodePipelineSource.git_hub(
                    "sendelivery/serverless-todo",
                    "main",
                ),
                commands=[
                    "chmod a+x ./scripts/pipeline/synth",
                    "./scripts/pipeline/synth",
                ],
            ),
        )

        application = ApplicationStage(
            self, f"{prefix}ApplicationStage", config, **kwargs
        )

        # Below we define custom pipeline steps required for the initial deployment of our web app,
        # and for subsequent Blue / Green deployments.

        # This repository is created in our stateful stack, unfortunately we can't use the actual
        # construct here as it doesn't exist when the pipeline is synthesized and thus would be
        # considered "crossing stage boundaries". However, the name, URI, and ARN can be
        # reliably determined using information we have.
        ecr_repo_uri = f"{self.account}.dkr.ecr.{self.region}.amazonaws.com/{config.image_repository_name}"
        ecr_repo_arn = f"arn:aws:ecr:{self.region}:{self.account}:repository/{config.image_repository_name}"

        # STEP: Build and upload a Docker image of our Next.js web app to ECR.
        # This step uses the pipeline's source file set by default (i.e. GitHub), meaning we don't
        # have to copy the web/ directory into cloud assembly file set during the synth step above.
        build_and_deploy_docker_image_step = pipelines.CodeBuildStep(
            f"{prefix}BuildAndUploadDockerImage",
            commands=[
                "chmod a+x ./scripts/pipeline/push_to_ecr",
                f"./scripts/pipeline/push_to_ecr {ecr_repo_uri}",
            ],
            role_policy_statements=[
                iam.PolicyStatement(
                    actions=[
                        "ecr:CompleteLayerUpload",
                        "ecr:UploadLayerPart",
                        "ecr:InitiateLayerUpload",
                        "ecr:BatchCheckLayerAvailability",
                        "ecr:PutImage",
                    ],
                    resources=[ecr_repo_arn],
                    effect=iam.Effect.ALLOW,
                ),
                iam.PolicyStatement(
                    actions=[
                        "ecr:GetAuthorizationToken",
                    ],
                    resources=["*"],
                    effect=iam.Effect.ALLOW,
                ),
            ],
        )

        # STEP: Generate templates required for a Blue / Green deployment of our web app.
        # This step runs the configure_deploy_step script that was copied into the cloud assembly
        # file set in the synth step.
        configure_deploy_step = pipelines.CodeBuildStep(
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
                "chmod a+x ./codedeploy/configure_deploy_step",
                f"./codedeploy/configure_deploy_step {prefix} {ecr_repo_uri}:latest",
            ],
        )

        # To configure our Blue Green deployment step we'll need to give it a reference to the
        # deployment group created in our web stack. To do this, we'll first grab a reference to
        # the CodeDeploy application via its name.
        cd_application = codedeploy.EcsApplication.from_ecs_application_name(
            self,
            id=f"{prefix}CodeDeployApplicationFromName",
            ecs_application_name=f"{prefix}DeploymentApplication",
        )

        # Next, we can grab the deployment group itself from the application.
        cd_deployment_group = (
            codedeploy.EcsDeploymentGroup.from_ecs_deployment_group_attributes(
                self,
                f"{prefix}ECSDeploymentGroupId",
                application=cd_application,
                deployment_group_name=f"{prefix}BlueGreenDeploymentGroup",
                deployment_config=config.deployment_config,
            )
        )

        # STEP: Run the Blue / Green deployment.
        # This replaces the current live "blue" container that's receiving traffic, with a "green"
        # one running the latest Docker image of our web app. This step is a custom Step from the
        # pipelines construct library.
        deploy_step = BlueGreenDeploymentStep(
            input_fileset=configure_deploy_step.primary_output,
            deployment_group=cd_deployment_group,
            prefix=prefix,
        )

        # Deploying a "green" version of our application is dependent on having the correct task
        # definition and app spec files.
        deploy_step.add_step_dependency(configure_deploy_step)

        # Now we can add the application stage, containing all our stacks, to the pipeline. Wiring
        # up the previously defined steps.

        pipeline.add_stage(
            application,
            stack_steps=[
                pipelines.StackSteps(
                    stack=application.web_stack,
                    pre=[build_and_deploy_docker_image_step],
                    post=[configure_deploy_step, deploy_step],
                ),
            ],
        )
