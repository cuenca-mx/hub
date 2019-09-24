import os
import boto3
import time

KINESIS_DYNAMO_TABLE = os.environ['KINESIS_DYNAMO_TABLE']
KINESIS_TTL_HOURS = os.environ['KINESIS_TTL_HOURS']
ACCESS_KEY = os.environ['ACCESS_KEY']
SECRET_KEY = os.environ['SECRET_KEY']
REGION_NAME = os.environ['REGION_NAME']

client_dynamo = boto3.client('dynamodb', region_name=REGION_NAME,
                             aws_access_key_id=ACCESS_KEY,
                             aws_secret_access_key=SECRET_KEY)


def write_to_db(key):
    try:
        ttl = int(time.time() + float(KINESIS_TTL_HOURS) * 3600)
        response = client_dynamo.put_item(
            TableName=KINESIS_DYNAMO_TABLE,
            Item={
                'uuid': {'S': key},
                'ttl': {'N': str(ttl)}
            },
            ReturnValues='ALL_OLD'
        )
        # Validate previously inserted
        old_value = response.get("Attributes")
        if old_value is not None:
            print('Duplicado: ', old_value)
            # Reset old value
            client_dynamo.put_item(
                TableName=KINESIS_DYNAMO_TABLE,
                Item=old_value
            )
            return False
        return True
    except Exception as e:
        print('Exception: ', e)
        return False
