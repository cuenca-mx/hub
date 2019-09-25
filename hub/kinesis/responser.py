from datetime import datetime
import json
import time

from hub.kinesis.client_kinesis import client


def put_response(response, stream_name: str):
    input_data = json.dumps(response)
    partition_key = '{}-{}'.format(
        stream_name, str(datetime.now().isoformat() + 'Z').replace(' ', '-'))

    try:
        response = client.put_record(
            StreamName=stream_name,
            Data=input_data,
            PartitionKey=partition_key
        )
        return response

    except client.exceptions.ResourceNotFoundException:
        time.sleep(1)
