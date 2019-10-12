import time

from hub.client import kinesis_client


def stream_is_active(stream_name: str) -> bool:
    try:
        stream_info = kinesis_client.describe_stream(StreamName=stream_name)
        description = stream_info.get('StreamDescription')
        response = description.get('StreamStatus') == 'ACTIVE'
    except kinesis_client.exceptions.ResourceNotFoundException:
        response = create_stream(stream_name)
    return response


def create_stream(stream_name: str) -> bool:
    try:
        kinesis_client.create_stream(StreamName=stream_name, ShardCount=1)
    except kinesis_client.exceptions.ResourceInUseException:
        time.sleep(1)
    status = stream_is_active(stream_name)
    if status != 'ACTIVE':
        time.sleep(1)
    return status
