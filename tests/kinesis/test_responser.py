import boto3
from moto import mock_kinesis

from hub.kinesis import put_response

STREAM = 'cuenca_stream'


@mock_kinesis
def test_responser():
    client = boto3.client('kinesis', region_name='us-east-2')
    client.create_stream(StreamName=STREAM, ShardCount=1)
    data = {
        "uuid": "f3296986-ded8-11e9-8000-000000000000",
        "task": "create_api_key",
        "headers": {},
        "body": {}
    }
    res = put_response(data, STREAM)
    assert res is not None
    assert res.get("ShardId") is not None
    assert res.get("SequenceNumber") is not None
