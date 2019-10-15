import os
import time

from hub.client import dynamo_client

KINESIS_DYNAMO_TABLE = os.getenv('KINESIS_DYNAMO_TABLE')
KINESIS_TTL_HOURS = os.getenv('KINESIS_TTL_HOURS', 24)


def write_to_db(key: str) -> bool:
    try:
        return insert_register(key)
    except dynamo_client.exceptions.ResourceNotFoundException:
        create_table()
        return insert_register(key)
    except ValueError as ex:
        if str(ex) == 'No table found':
            create_table()
            return insert_register(key)
        else:
            raise ex


def create_table():
    dynamo_client.create_table(
        TableName=KINESIS_DYNAMO_TABLE,
        KeySchema=[{'AttributeName': 'uuid', 'KeyType': 'HASH'}],
        AttributeDefinitions=[{'AttributeName': 'uuid', 'AttributeType': 'S'}],
        BillingMode='PROVISIONED',
        ProvisionedThroughput={
            'ReadCapacityUnits': 30,
            'WriteCapacityUnits': 30,
        },
    )
    waiter = dynamo_client.get_waiter('table_exists')
    waiter.wait(
        TableName=KINESIS_DYNAMO_TABLE,
        WaiterConfig={'Delay': 1, 'MaxAttempts': 120},
    )

    dynamo_client.update_time_to_live(
        TableName=KINESIS_DYNAMO_TABLE,
        TimeToLiveSpecification={'Enabled': True, 'AttributeName': 'ttl'},
    )


def insert_register(key: str) -> bool:
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
