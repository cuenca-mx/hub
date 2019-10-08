from typing import Dict
from unittest.mock import Mock

import boto3
import pytest
from moto import mock_dynamodb2, mock_kinesis

from hub.db.dynamo import KINESIS_DYNAMO_TABLE
from hub.kinesis.decorators import hub_task
from hub.kinesis.producer import Producer
from hub.workers import init_workers

STREAM = 'stream_name'


@mock_kinesis
@mock_dynamodb2
def test_produce_succesful_response():
    # Create table in dynamoDb for idempotency
    client = boto3.client('dynamodb', region_name='us-east-2')

    client.create_table(
        TableName=KINESIS_DYNAMO_TABLE,
        KeySchema=[{'AttributeName': 'uuid', 'KeyType': 'HASH'}],
        AttributeDefinitions=[
            {'AttributeName': 'uuid', 'AttributeType': 'S'},
            {'AttributeName': 'ttl', 'AttributeType': 'N'},
        ],
    )

    # Create module with tasks
    module = Mock()

    @hub_task(STREAM)
    def sum_function(data: Dict):
        return data['a'] + data['b']

    module.sum_function = sum_function

    # Init workers
    init_workers(module, 1)

    # Produce data and wait for the response
    producer = Producer('stream_name')
    data = dict(a=1, b=1)
    answer = producer.produce(data, 'sum_function')

    assert answer == 2


@mock_kinesis
def test_produce_timeout():
    # Produce data and wait for the response, there is no listener this time
    producer = Producer('stream_name')
    data = dict(a=1, b=1)
    with pytest.raises(TimeoutError):
        producer.produce(data, 'sum_function')
