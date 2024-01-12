from botocore.exceptions import ClientError
import json
import logging
from tododb_utils import get_table
import uuid


logger = logging.getLogger(__name__)
table = get_table(logger)


def handler(event, context):
    logger.info(event, context)

    item = json.loads(event["body"])

    if event["requestContext"]["httpMethod"] == "POST":
        response = create_item(item, table, logger)
    elif event["requestContext"]["httpMethod"] == "PUT":
        response = update_item(item, table, logger)
    else:
        logger.info("Unsupported HTTP Method", event["requestContext"])

    return {
        "statusCode": 200,
        "headers": {"Content-Type": "text/plain"},
        "body": response,
    }


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
