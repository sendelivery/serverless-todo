from constructs import Construct
from aws_cdk import (
    Duration,
    aws_elasticloadbalancingv2 as elb,
    aws_codedeploy as codedeploy,
    aws_iam as iam,
)
from aws_cdk.aws_ec2 import IVpc
from aws_cdk.aws_ecs_patterns import ApplicationLoadBalancedServiceBase
from config import CommonConfig


class BlueGreenEcsCodedeploy(Construct):
    """This construct defines the resources required for a Blue / Green deployment of an ECS
    application.

    It provisions a CodeDeploy application and deployment group, as well as a "green" LB target
    group.
    """

    def __init__(
        self,
        scope: Construct,
        id: str,
        service: ApplicationLoadBalancedServiceBase,
        vpc: IVpc,
        config: CommonConfig,
        **kwargs,
    ) -> None:
        """Defines the resources required for a Code Deploy managed blue / green deployment of an
        ECS application.

        Args:
            scope (Construct): The construct's parent or owner. This can either be a stack or
            another construct.
            id (str): The scoped ID of this construct.
            service: (ApplicationLoadBalancedServiceBase): The service we wish to configure a blue
            / green deployment for.
            vpc (IVpc): The VPC our service is deployed in, used to configure "green" target groups.
            config (CommonConfig): A user-defined configuration data class.
        """
        super().__init__(scope, id, **kwargs)

        prefix = config.prefix

        codedeploy_application = codedeploy.EcsApplication(
            self,
            f"{prefix}DeploymentApplication",
            application_name=f"{prefix}DeploymentApplication",
        )

        # Define the "green" target group and listener that our ALB will use to route canary
        # traffic.
        # We'll omit a target group name to prevent confusion once the target groups have been
        # switched over in the ALB.
        green_target_group = elb.ApplicationTargetGroup(
            self,
            f"{prefix}GreenTargetGroup",
            protocol=elb.ApplicationProtocol.HTTP,
            target_type=elb.TargetType.IP,
            health_check=elb.HealthCheck(
                healthy_http_codes="200",
                path="/health",
                interval=Duration.minutes(5),
            ),
            vpc=vpc,
        )

        green_listener = service.load_balancer.add_listener(
            f"{prefix}GreenListener",
            port=8080,
            protocol=elb.ApplicationProtocol.HTTP,
            default_target_groups=[green_target_group],
        )

        # TODO how much of this is actually required by our deployment group?
        codedeploy_execution_role_policies = [
            iam.ManagedPolicy.from_aws_managed_policy_name("CloudWatchLogsFullAccess"),
            iam.ManagedPolicy.from_aws_managed_policy_name("AWSCodeDeployRoleForECS"),
            iam.ManagedPolicy.from_aws_managed_policy_name("AmazonECS_FullAccess"),
            iam.ManagedPolicy.from_aws_managed_policy_name(
                "AWSCodeBuildDeveloperAccess"
            ),
            iam.ManagedPolicy.from_aws_managed_policy_name(
                "AmazonEC2ContainerRegistryFullAccess"
            ),
            iam.ManagedPolicy.from_aws_managed_policy_name(
                "service-role/AWSLambdaBasicExecutionRole"
            ),
        ]

        # This is the execution role used by the CodeDeploy deployment group.
        # A deployment group is a collection of compute instances targeted for deployment.
        codedeploy_execution_role = iam.Role(
            self,
            f"{prefix}BGDeploymentExecutionRole",
            role_name=f"{prefix}BGDeploymentExecutionRole",
            assumed_by=iam.ServicePrincipal("codedeploy.amazonaws.com"),
            managed_policies=codedeploy_execution_role_policies,
        )

        codedeploy.EcsDeploymentGroup(
            self,
            f"{prefix}BlueGreenDeploymentGroup",
            deployment_group_name=f"{prefix}BlueGreenDeploymentGroup",
            application=codedeploy_application,
            service=service.service,
            role=codedeploy_execution_role,
            blue_green_deployment_config=codedeploy.EcsBlueGreenDeploymentConfig(
                blue_target_group=service.target_group,
                green_target_group=green_target_group,
                listener=service.listener,
                test_listener=green_listener,
                deployment_approval_wait_time=config.deployment_approval_wait_time,
                termination_wait_time=config.deployment_termination_wait_time,
            ),
            deployment_config=config.deployment_config,
        )
