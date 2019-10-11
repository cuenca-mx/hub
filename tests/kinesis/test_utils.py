import boto3
from moto import mock_dynamodb2

from hub.db.dynamo import KINESIS_DYNAMO_TABLE
from hub.kinesis.decorators import hub_task

STREAM = 'cuenca_stream'


@mock_dynamodb2
def test_hub_task():
    client = boto3.client('dynamodb', region_name='us-east-2')

    client.create_table(
        TableName=KINESIS_DYNAMO_TABLE,
        KeySchema=[{'AttributeName': 'uuid', 'KeyType': 'HASH'}],
        AttributeDefinitions=[
            {'AttributeName': 'uuid', 'AttributeType': 'S'},
            {'AttributeName': 'ttl', 'AttributeType': 'N'},
        ],
    )

    data = dict(
        uuid="f3296986-ded8-11e9-8000-000000000000",
        task="create_api_key",
        headers=dict(),
        body=dict(),
    )

    # Decorated function
    @hub_task(STREAM)
    def mock_function(record):
        return dict(greeting="I'm healthy!!!")

    # Custom attribute
    assert getattr(mock_function, "hub_task") == STREAM

    # Task processed 1st time
    task_result = mock_function(data)
    assert task_result.get("greeting") == "I'm healthy!!!"
