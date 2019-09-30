import boto3
import json
from moto import mock_kinesis

from hub import Worker
from hub.kinesis import Listener, put_response, DataKinesis

STREAM = 'cuenca_stream'
STREAM_REQ = STREAM + '.request'
STREAM_RES = STREAM + '.response'
N_WORKERS = 2


@mock_kinesis
def test_worker():
    client = boto3.client('kinesis', region_name='us-east-2')
    data = DataKinesis(
        uuid="f3296986-ded8-11e9-8000-000000000000",
        task="create_api_key",
        headers={},
        body={}
    )

    # Callback for record
    def process_records(record):
        return record

    w = Worker(STREAM, process_records, None, N_WORKERS)
    threads = w.start()

    # Streams created
    list_stream = client.list_streams().get("StreamNames")
    assert STREAM_REQ in list_stream
    assert STREAM_RES in list_stream

    # Threads listeners created
    assert len(threads) == N_WORKERS
    for t in threads:
        assert t.isAlive()
