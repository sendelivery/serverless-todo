#!/usr/bin/env python3
import os
import aws_cdk as cdk
from app.stateful.stateful_stack import StatefulStack
from app.stateless.stateless_stack import StatelessStack


app = cdk.App()

stateful_stack = StatefulStack(
    app,
    "TodoDbStack",
    env=cdk.Environment(
        account=os.getenv("CDK_DEFAULT_ACCOUNT"), region=os.getenv("CDK_DEFAULT_REGION")
    ),
)

StatelessStack(
    app,
    "TodoApiStack",
    entries_table=stateful_stack.entries_table,
    env=cdk.Environment(
        account=os.getenv("CDK_DEFAULT_ACCOUNT"), region=os.getenv("CDK_DEFAULT_REGION")
    ),
)

app.synth()
