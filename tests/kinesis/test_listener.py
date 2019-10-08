import boto3
from moto import mock_kinesis

from hub.kinesis.data_kinesis import DataKinesis
from hub.kinesis.listener import Listener
from hub.kinesis.producer import Producer

STREAM = 'cuenca_stream'
STREAM_REQ = STREAM + '.request'
STREAM_RES = STREAM + '.response'


@mock_kinesis
def test_listener():
    client = boto3.client('kinesis', region_name='us-east-2')
    data = DataKinesis(
        uuid="f3296986-ded8-11e9-8000-000000000000",
        task="create_api_key",
        headers={},
        body={},
    )

    # Callback for record
    def process_records(record):
        assert record.get("uuid") == data.uuid

    # Create streams and listener
    listener = Listener(STREAM, process_records, 1)
    list_stream = client.list_streams().get("StreamNames")
    assert STREAM_REQ in list_stream
    assert STREAM_RES in list_stream
    # Receive data. Listen and execute callback
    Producer.put_data(data.to_dict(), STREAM_REQ)
    listener.run()
