from dataclasses import dataclass
from aws_cdk import Duration, RemovalPolicy
from aws_cdk.aws_ecr import LifecycleRule
from aws_cdk.aws_ecs import DeploymentControllerType
from aws_cdk.aws_logs import RetentionDays
from aws_cdk.aws_codedeploy import EcsDeploymentConfig


@dataclass
class CommonConfig:
    # General configuration
    ephemeral: bool = False
    prefix: str = "Todo"
    removal_policy: RemovalPolicy = RemovalPolicy.RETAIN
    log_retention: RetentionDays = RetentionDays.INFINITE
    # Stateful stack configuration
    image_repository_name: str = f"{prefix.lower()}-image-repo"
    auto_delete_images: bool = False
    ecr_lifecycle_rule: LifecycleRule | None = None
    # Web stack configuration
    web_deployment_controller_type: DeploymentControllerType | None = (
        DeploymentControllerType.CODE_DEPLOY
    )
    # Blue / Green configuration
    deployment_approval_wait_time = Duration.minutes(10)
    deployment_termination_wait_time = Duration.minutes(5)
    deployment_config = EcsDeploymentConfig.CANARY_10_PERCENT_5_MINUTES
