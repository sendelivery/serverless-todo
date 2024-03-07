from botocore.exceptions import ClientError
import json
import logging
from tododb_utils import get_table
import uuid


logger = logging.getLogger(__name__)
table = get_table(logger)


def handler(event, context):
    logger.info(f"Event: {event}")
    logger.info(f"Context: {context}")

    entry = json.loads(event["body"])

    if event["requestContext"]["httpMethod"] == "POST":
        response = create_entry(entry)
    elif event["requestContext"]["httpMethod"] == "PUT":
        response = update_entry(entry)
    else:
        logger.info("Unsupported HTTP Method", event["requestContext"])

    return {
        "statusCode": 200,
        "headers": {"Content-Type": "text/plain"},
        "body": response,
    }


def create_entry(entry):
    try:
        id = str(uuid.uuid4())
        table.put_item(
            Item={
                "Id": id,
                "DateCreated": entry["DateCreated"],
                "Description": entry["Description"],
                "Completed": entry["Completed"],
            }
        )
        logger.info(f"Created entry with Id: {id}, and attributes: {entry}")
        return id
    except ClientError as err:
        logger.error(
            "Failed when posting new entry due to: %s: %s",
            err.response["Error"]["Code"],
            err.response["Error"]["Message"],
        )
        raise


def update_entry(entry):
    try:
        id = entry["Id"]

        table.update_item(
            Key={"Id": id},
            UpdateExpression="SET Completed = :val1",
            ExpressionAttributeValues={":val1": entry["Completed"]},
        )
        logger.info(f"Updated entry with Id: {id} to Completed: {entry['Completed']}")
        return f"Successfully updated entry {id}"
    except ClientError as err:
        logger.error(
            "Failed when posting new entry due to: %s: %s",
            err.response["Error"]["Code"],
            err.response["Error"]["Message"],
        )
        raise
