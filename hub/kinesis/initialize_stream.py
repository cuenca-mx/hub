import time

from hub.kinesis.client_kinesis import client


def check_status_stream(stream_name):
    try:
        stream_info = client.describe_stream(StreamName=stream_name)
        description = stream_info.get('StreamDescription')
        status = description.get('StreamStatus')
    except client.exceptions.ResourceNotFoundException:
        status = create_stream(stream_name)

    return status


def create_stream(stream_name):
    try:
        client.create_stream(StreamName=stream_name, ShardCount=1)

    except client.exceptions.ResourceInUseException:
        time.sleep(1)

    status = check_status_stream(stream_name)
    if status != 'ACTIVE':
        time.sleep(1)
    return status
