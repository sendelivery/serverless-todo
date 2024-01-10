import boto3
from botocore.exceptions import ClientError
import json
import logging
import os

logger = logging.getLogger(__name__)
dyn = boto3.resource("dynamodb")
table_name = os.environ["TABLE_NAME"]


def handler(event, context):
    items = []

    table = get_table()

    try:
        scan_kwargs = {}

        done = False
        start_key = None
        while not done:
            if start_key:
                scan_kwargs["ExclusiveStartKey"] = start_key
            response = table.scan(**scan_kwargs)
            items.extend(response.get("Items", []))
            start_key = response.get("LastEvaluatedKey", None)
            done = start_key is None
    except ClientError as err:
        logger.error(
            "Failed when scanning for items due to: %s: %s",
            err.response["Error"]["Code"],
            err.response["Error"]["Message"],
        )
        raise

    # Convert the decimals that come out of Dynamo into JSON serialisable integers
    for item in items:
        item["Id"] = int(item["Id"])
        item["DateCreated"] = int(item["DateCreated"])

    items = sorted(items, key=lambda x: x["DateCreated"])

    return {
        "statusCode": 200,
        "body": json.dumps({"data": items}),
    }


def get_table():
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
