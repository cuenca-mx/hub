import json
from datetime import datetime

from hub import kinesis_client


def put_response(response: str, stream_name: str) -> bool:
    input_data = json.dumps(response)
    partition_key = '{}-{}'.format(
        stream_name, str(datetime.now().isoformat() + 'Z').replace(' ', '-')
    )

    kinesis_client.put_record(
        StreamName=stream_name, Data=input_data, PartitionKey=partition_key
    )

    return True
