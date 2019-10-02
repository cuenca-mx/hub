from unittest.mock import Mock

import boto3
from moto import mock_dynamodb2, mock_kinesis

from hub import init_workers
from hub.kinesis.utils import kinesis_task

STREAM = 'cuenca_stream'
STREAM_REQ = STREAM + '.request'
STREAM_RES = STREAM + '.response'


@mock_dynamodb2
@mock_kinesis
def test_init_workers():
    client = boto3.client('kinesis', region_name='us-east-2')

    # Create Module with tasks
    module = Mock()

    @kinesis_task(STREAM)
    def mock_function(record):
        return dict(greeting="I'm healthy!!!")

    module.mock_function = mock_function

    # Init Workers
    workers = init_workers(module, 1)

    # Streams created
    list_stream = client.list_streams().get("StreamNames")
    assert STREAM_REQ in list_stream
    assert STREAM_RES in list_stream
    # Task assigned
    assert workers[0].stream_name == STREAM
    assert mock_function.__eq__(workers[0].task_list.get(STREAM))
