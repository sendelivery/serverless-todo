#!/usr/bin/env python3
import os
from aws_cdk import (
    App,
    Environment,
    RemovalPolicy,
)
from pipeline.pipeline_stack import (
    ServerlessTodoPipelineStack,
    ServerlessTodoPipelineStage,
)

app = App()

ServerlessTodoPipelineStack(
    app,
    "TodoPipelineStack",
    env=Environment(
        account=os.getenv("CDK_DEFAULT_ACCOUNT"), region=os.getenv("CDK_DEFAULT_REGION")
    ),
)

# The below stage exist purely for developers to create ephemeral environmenst using the deploy_ephemeral script.
prefix = app.node.try_get_context("ephemeral_prefix")
prefix = "DefaultPrefix-Todo" if prefix is None else prefix

ServerlessTodoPipelineStage(
    app,
    f"{prefix}Stage",
    prefix=prefix,
    stateful_removal_policy=RemovalPolicy.DESTROY,
)

app.synth()
