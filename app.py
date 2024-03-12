#!/usr/bin/env python3
import os
from aws_cdk import App, Environment, RemovalPolicy
from aws_cdk.aws_logs import RetentionDays
from aws_cdk.aws_ecr import LifecycleRule

from pipeline.pipeline_stack import PipelineStack
from application.networking import NetworkingStack
from application.stateful import StatefulStack
from application.stateless import StatelessStack
from application.web import WebStack
from config import CommonConfig

app = App()

PipelineStack(
    app,
    "TodoPipelineStack",
    config=CommonConfig(),
    env=Environment(
        account=os.getenv("CDK_DEFAULT_ACCOUNT"), region=os.getenv("CDK_DEFAULT_REGION")
    ),
)

# The below stacks will only synthesize if we supply the required context, which should only be
# done via the deploy_ephemeral script.
prefix = app.node.try_get_context("ephemeral_prefix")

if prefix is not None:
    ephemeral_config = CommonConfig(
        ephemeral=True,
        prefix=prefix,
        removal_policy=RemovalPolicy.DESTROY,
        log_retention=RetentionDays.FIVE_DAYS,
        auto_delete_images=True,
        ecr_lifecycle_rule=[LifecycleRule(max_image_count=1)],
        web_deployment_controller_type=None,
    )

    networking = NetworkingStack(app, f"{prefix}NetworkingStack", ephemeral_config)

    stateful = StatefulStack(app, f"{prefix}StatefulStack", ephemeral_config)

    stateless = StatelessStack(
        app,
        f"{prefix}StatelessStack",
        entries_table=stateful.entries_table,
        vpc=networking.vpc,
        vpc_endpoint=networking.vpc_interface_endpoint,
        config=ephemeral_config,
    )

    web_stack = WebStack(
        app,
        f"{prefix}WebStack",
        api=stateless.api,
        vpc=networking.vpc,
        ecr_repo=stateful.ecr_repository,
        config=ephemeral_config,
    )


app.synth()
