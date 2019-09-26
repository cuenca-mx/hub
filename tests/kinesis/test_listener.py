import boto3
import json
from moto import mock_kinesis
from hub.kinesis import Listener, put_response, DataKinesis

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
        body={}
    )

    # Callback for record
    def process_records(record):
        stream_data = json.loads(record.get("Data").decode())
        assert stream_data.get("uuid") == data.uuid

    # Create streams and listener
    listener = Listener(STREAM, process_records, 1)
    list_stream = client.list_streams().get("StreamNames")
    assert STREAM_REQ in list_stream
    assert STREAM_RES in list_stream
    # Receive data. Listen and execute callback
    put_response(data.to_dict(), STREAM_REQ)
    listener.run()
