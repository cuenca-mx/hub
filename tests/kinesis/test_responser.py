import boto3
import pytest
from moto import mock_kinesis

from hub import kinesis_client
from hub.kinesis.producer import Producer

STREAM = 'cuenca_stream'


@mock_kinesis
def test_put_response():
    client = boto3.client('kinesis', region_name='us-east-2')
    client.create_stream(StreamName=STREAM, ShardCount=1)
    data = {
        "uuid": "f3296986-ded8-11e9-8000-000000000000",
        "task": "create_api_key",
        "headers": {},
        "body": {},
    }
    res = Producer.put_data(data, STREAM)
    assert res


@mock_kinesis
def test_put_response_fail():
    data = {
        "uuid": "f3296986-ded8-11e9-8000-000000000000",
        "task": "create_api_key",
        "headers": {},
        "body": {},
    }
    # Stream has not been created
    with pytest.raises(kinesis_client.exceptions.ResourceNotFoundException):
        Producer.put_data(data, STREAM)
