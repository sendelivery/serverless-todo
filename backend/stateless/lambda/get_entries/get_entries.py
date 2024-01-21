from botocore.exceptions import ClientError
import json
import logging
from tododb_utils import get_table


logger = logging.getLogger(__name__)
table = get_table(logger)


def handler(event, context):
    items = []

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

    # Convert the decimal date that come out of Dynamo into a JSON serialisable integer
    for item in items:
        item["DateCreated"] = int(item["DateCreated"])

    items = sorted(items, key=lambda x: x["DateCreated"])

    return {
        "statusCode": 200,
        "body": json.dumps(items),
    }
