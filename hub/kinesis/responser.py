from datetime import datetime
import json
import time

from hub.kinesis.client_kinesis import client


def put_response(response, stream_name_response: str):
        input_data = json.dumps(response)
        partition_key = '{}-{}'.format(
            stream_name_response,
            str(datetime.now().isoformat() + 'Z').replace(' ', '-'))

        try:
            client.put_record(
                StreamName=stream_name_response,
                Data=input_data,
                PartitionKey=partition_key
            )

        except client.exceptions.ResourceNotFoundException:
            time.sleep(1)
