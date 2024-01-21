#!/usr/bin/env python3
import os
import aws_cdk as cdk

from pipeline.pipeline_stack import ServerlessTodoPipelineStack

app = cdk.App()

ServerlessTodoPipelineStack(
    app,
    "ServerlessTodoPipelineStack",
    env=cdk.Environment(
        account=os.getenv("CDK_DEFAULT_ACCOUNT"), region=os.getenv("CDK_DEFAULT_REGION")
    ),
)

# stateful_stack = StatefulStack(
#     app,
#     "TodoDbStack",
#     env=cdk.Environment(
#         account=os.getenv("CDK_DEFAULT_ACCOUNT"), region=os.getenv("CDK_DEFAULT_REGION")
#     ),
# )

# StatelessStack(
#     app,
#     "TodoApiStack",
#     entries_table=stateful_stack.entries_table,
#     env=cdk.Environment(
#         account=os.getenv("CDK_DEFAULT_ACCOUNT"), region=os.getenv("CDK_DEFAULT_REGION")
#     ),
# )

app.synth()
