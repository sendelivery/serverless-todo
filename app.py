#!/usr/bin/env python3
import os
from aws_cdk import (
    App,
    Environment,
    RemovalPolicy,
)
from pipeline.pipeline_stack import (
    ServerlessTodoPipelineStack,
    ApplicationStage,
)

app = App()

ServerlessTodoPipelineStack(
    app,
    "TodoPipelineStack",
    prefix="Todo",
    env=Environment(
        account=os.getenv("CDK_DEFAULT_ACCOUNT"), region=os.getenv("CDK_DEFAULT_REGION")
    ),
)

# The below stage exists purely for developers to create ephemeral environments using the
# deploy_ephemeral script. It will only synthesize if we supply the required context.
prefix = app.node.try_get_context("ephemeral_prefix")
if prefix:
    ApplicationStage(
        app,
        f"{prefix}Stage",
        prefix=prefix,
        stateful_removal_policy=RemovalPolicy.DESTROY,
    )


app.synth()
