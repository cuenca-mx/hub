import time

from boto.kinesis.exceptions import (ResourceInUseException,
                                     ResourceNotFoundException)

from hub import kinesis_client


def stream_is_active(stream_name: str) -> bool:
    try:
        stream_info = kinesis_client.describe_stream(StreamName=stream_name)
        description = stream_info.get('StreamDescription')
        response = description.get('StreamStatus') == 'ACTIVE'
    except ResourceNotFoundException:
        response = False
    return response


def create_stream(stream_name: str) -> bool:
    try:
        kinesis_client.create_stream(StreamName=stream_name, ShardCount=1)
    except ResourceInUseException:
        time.sleep(1)
    status = check_status_stream(stream_name)
    return status
