import boto3
from moto import mock_kinesis

from hub.kinesis.helpers import create_stream, stream_is_active

STREAM = 'cuenca_stream'


@mock_kinesis
def test_check_status_stream():
    client = boto3.client('kinesis', region_name='us-east-2')
    client.create_stream(StreamName=STREAM, ShardCount=1)
    status = stream_is_active(STREAM)
    assert status


@mock_kinesis
def test_create_stream():
    client = boto3.client('kinesis', region_name='us-east-2')
    status = create_stream(STREAM)
    assert status

    # Try to duplicate streams
    status = create_stream(STREAM)
    assert status

    # Only one has been created
    list_stream = client.list_streams().get("StreamNames")
    assert STREAM in list_stream
    assert len(list_stream) == 1
