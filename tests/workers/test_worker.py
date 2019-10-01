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

    # Callback for new records
    def task_function(record):
        return "Result OK"

    def other_task(record):
        return "Other Result"

    tasks_list = dict(
        task_name=task_function,
        other_name=other_task
    )
    w = Worker(STREAM, tasks_list, None, N_WORKERS)
    threads = w.start()

    # Streams created
    list_stream = client.list_streams().get("StreamNames")
    assert STREAM_REQ in list_stream
    assert STREAM_RES in list_stream

    # Threads listeners created
    assert len(threads) == N_WORKERS
    for t in threads:
        assert t.isAlive()


@mock_kinesis
def test_process_records():
    client = boto3.client('kinesis', region_name='us-east-2')

    # Task for new records
    def registered_task(record):
        return "OK"

    tasks_list = dict(
        registered_task=registered_task,
    )

    w = Worker(STREAM, tasks_list, None, N_WORKERS)
    w.start()

    record_ok = {
        'SequenceNumber': '1',
        'Data': b'{'
                b'"uuid": "f3296986-ded8-11e9-8000-000000000000", '
                b'"task": "registered_task", '
                b'"headers": {}, '
                b'"body": {}'
                b'}',
    }
    record_missing_task = {
        'SequenceNumber': '2',
        'Data': b'{'
                b'"uuid": "t89876702-cas9-22g1-9000-000000000000", '
                b'"task": "missing_task", '
                b'"headers": {}, '
                b'"body": {}'
                b'}',
    }
    record_malformed = {
        'SequenceNumber': '3',
        'Data': b'{"name": "Rogelio"}',
    }

    # Correct
    response = w.process_records(record_ok)
    assert response == "OK"

    # Task function not found
    response = w.process_records(record_missing_task)
    assert response is None

    # Malformed record
    response = w.process_records(record_malformed)
    assert response is None
