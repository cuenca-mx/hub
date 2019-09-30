import datetime
import pickle
from unittest.mock import Mock

import boto3
from jsonpickle import json
from moto import mock_dynamodb2, mock_kinesis

from hub import find_decorated_functions, task_selector, init_workers
from hub.kinesis.utils import kinesis_task

STREAM = 'cuenca_stream'


@mock_dynamodb2
def test_find_decorated_function():
    module = Mock()
    # Decorated function
    @kinesis_task(STREAM)
    def mock_function(record):
        return dict(greeting="I'm healthy!!!")

    module.mock_function = mock_function
    res = find_decorated_functions(module)

    stream = res.get(STREAM)
    assert stream is not None
    assert mock_function.__eq__(stream.get("mock_function"))


def test_task_selector():

    def registered_task(record):
        return "Result OK"

    def other_task(record):
        return "Other Result"

    # Record Kinesis Info
    # https://docs.aws.amazon.com/es_es/kinesis/latest/APIReference/API_Record.html
    record_ok = {
        'SequenceNumber': '1',
        'Data': b'{'
                b'"uuid": "f3296986-ded8-11e9-8000-000000000000", '
                b'"task": "registered_task", '
                b'"headers": {}, '
                b'"body": {}'
                b'}',
    }
    record_error = {
        'SequenceNumber': '1',
        'Data': b'{'
                b'"uuid": "t89876702-cas9-22g1-9000-000000000000", '
                b'"task": "missing_task", '
                b'"headers": {}, '
                b'"body": {}'
                b'}',
    }
    # Group of Task
    tasks = dict(
        registered_task=registered_task,
        other_task=other_task
    )
    selector = task_selector(tasks)

    # Find a function "task" to execute
    response_ok = selector(record_ok)
    assert response_ok == "Result OK"

    # Function not found
    response_err = selector(record_error)
    assert response_err is None
