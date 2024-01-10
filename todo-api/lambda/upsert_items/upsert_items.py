import boto3
from botocore.exceptions import ClientError
import json
import logging
import os
import uuid

dyn = boto3.resource("dynamodb")
table_name = os.environ["TABLE_NAME"]


def handler(event, context):
    logger = logging.getLogger(__name__)

    print("event: {}".format(json.dumps(event)))
    print(context)

    table = get_table(logger)
    item = json.loads(event["body"])

    if event["requestContext"]["httpMethod"] == "POST":
        response = create_item(item, table, logger)
    elif event["requestContext"]["httpMethod"] == "PUT":
        response = update_item(item, table, logger)
    else:
        logger.info("Unsupported HTTP Method", event)

    return {
        "statusCode": 200,
        "headers": {"Content-Type": "text/plain"},
        "body": response,
    }


def get_table(logger):
    """
    Determines if our table exists and returns it to the caller if it does.
    """
    try:
        table = dyn.Table(table_name)
        table.load()
    except ClientError as err:
        logger.error(
            "Ran into an error when trying to get table %s. %s: %s",
            table_name,
            err.response["Error"]["Code"],
            err.response["Error"]["Message"],
        )
        raise

    return table


def create_item(item, table, logger):
    try:
        id = str(uuid.uuid4())
        table.put_item(
            Item={
                "Id": id,
                "DateCreated": item["DateCreated"],
                "Description": item["Description"],
                "Completed": item["Completed"],
            }
        )
        logger.info(f"Created item with Id: {id}, and attributes: {item}")
        return id
    except ClientError as err:
        logger.error(
            "Failed when posting new item due to: %s: %s",
            err.response["Error"]["Code"],
            err.response["Error"]["Message"],
        )
        raise


def update_item(item, table, logger):
    try:
        id = item["Id"]

        table.update_item(
            Key={"Id": id},
            UpdateExpression="SET Completed = :val1",
            ExpressionAttributeValues={":val1": item["Completed"]},
        )
        logger.info(f"Updated item with Id: {id} to Completed: {item['Completed']}")
        return f"Successfully updated item {id}"
    except ClientError as err:
        logger.error(
            "Failed when posting new item due to: %s: %s",
            err.response["Error"]["Code"],
            err.response["Error"]["Message"],
        )
        raise
