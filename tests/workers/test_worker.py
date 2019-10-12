import boto3
from moto import mock_dynamodb2, mock_kinesis

from hub.workers import Worker

STREAM = 'cuenca_stream'
STREAM_REQ = STREAM + '.request'
STREAM_RES = STREAM + '.response'
N_WORKERS = 2


@mock_kinesis
def test_worker():
    client = boto3.client('kinesis', region_name='us-east-2')

    # Callback for new records
    def task_function(_):
        return "Result OK"

    def other_task(_):
        return "Other Result"

    tasks_list = dict(task_name=task_function, other_name=other_task)
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
@mock_dynamodb2
def test_process_records():
    # Task for new records
    def registered_task(_):
        return dict(greeting='OK')

    tasks_list = dict(registered_task=registered_task)
    w = Worker(STREAM, tasks_list, None, N_WORKERS)

    record_ok = dict(
        uuid='f3296986-ded8-11e9-8000-000000000000',
        task='registered_task',
        headers=dict(),
        body=dict(),
    )

    record_missing_task = dict(
        uuid='t89876702-cas9-22g1-9000-000000000000',
        task='missing_task',
        headers=dict(),
        body=dict(),
    )

    record_malformed = {'SequenceNumber': '3', 'Data': b'sample_string'}

    # Correct
    response = w.process_records(record_ok)
    assert response.get('body').get('greeting') == 'OK'

    # Task function not found
    response = w.process_records(record_missing_task)
    assert response.get('body').get('error') == 'Task not implemented'

    # Malformed record
    response = w.process_records(record_malformed)
    assert response.get('body').get('error') == 'UUID not assigned'
