import os
import time

from hub.client import dynamo_client

KINESIS_DYNAMO_TABLE = os.environ['KINESIS_DYNAMO_TABLE']
KINESIS_TTL_HOURS = os.getenv('KINESIS_TTL_HOURS', 24)


def write_to_db(key: str) -> bool:
    ttl = int(time.time() + float(KINESIS_TTL_HOURS) * 3600)
    response = dynamo_client.put_item(
        TableName=KINESIS_DYNAMO_TABLE,
        Item={'uuid': {'S': key}, 'ttl': {'N': str(ttl)}},
        ReturnValues='ALL_OLD',
    )
    # Validate previously inserted
    old_value = response.get("Attributes")
    if old_value is not None and old_value != {}:
        # Reset old value
        dynamo_client.put_item(TableName=KINESIS_DYNAMO_TABLE, Item=old_value)
        return False
    return True
