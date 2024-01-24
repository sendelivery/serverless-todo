import aws_cdk as core
import aws_cdk.assertions as assertions

from backend.stateful.stateful_stack import StatefulStack
# from app.todo_api_stack import TodoApiStack


def test_dynamodb_table_created():
    app = core.App()
    stateful_stack = StatefulStack(app, "db")
    dbtemplate = assertions.Template.from_stack(stateful_stack)

    # stack = TodoApiStack(app, "backend", table=stateful_stack.entries_table)
    # template = assertions.Template.from_stack(stack)

    dbtemplate.has_resource_properties(
        "AWS::DynamoDB::Table",
        {
            "KeySchema": [{"AttributeName": "Id", "KeyType": "HASH"}],
        },
    )
