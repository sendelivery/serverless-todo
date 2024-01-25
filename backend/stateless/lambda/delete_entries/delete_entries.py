from botocore.exceptions import ClientError
import json
import logging
from tododb_utils import get_table


logger = logging.getLogger(__name__)
table = get_table(logger)


def handler(event, context):
    logger.info(event, context)

    body = json.loads(event["body"])
    id = body["Id"]

    try:
        table.delete_item(Key={"Id": id})
        logger.info(f"Deleted entry with Id: {id}")
    except ClientError as err:
        logger.error(
            "Failed when deleting new entry due to: %s: %s",
            err.response["Error"]["Code"],
            err.response["Error"]["Message"],
        )
        raise

    return {"statusCode": 200, "headers": {"Content-Type": "text/plain"}}
