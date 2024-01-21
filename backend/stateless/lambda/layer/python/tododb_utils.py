import boto3
from botocore.exceptions import ClientError
import os


dynamo_resource = boto3.resource("dynamodb")


def get_table(logger):
    """
    Determines if our table exists and returns it to the caller if it does.
    """
    table_name = os.environ["TABLE_NAME"]

    try:
        table = dynamo_resource.Table(table_name)
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
