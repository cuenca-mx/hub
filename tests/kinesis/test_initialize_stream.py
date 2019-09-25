import boto3
from moto import mock_kinesis

from hub.kinesis.initialize_stream import check_status_stream, create_stream

STREAM = 'cuenca_stream'


@mock_kinesis
def test_check_status_stream():
    client = boto3.client('kinesis', region_name='us-east-2')
    client.create_stream(StreamName=STREAM, ShardCount=1)
    status = check_status_stream(STREAM)
    assert status == "ACTIVE"


@mock_kinesis
def test_create_stream():
    client = boto3.client('kinesis', region_name='us-east-2')
    status = create_stream(STREAM)
    assert status == "ACTIVE"
    list_stream = client.list_streams().get("StreamNames")
    assert STREAM in list_stream
