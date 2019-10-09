import json
import time
import uuid
from datetime import datetime
from typing import Dict

import timeout_decorator
from boto.kinesis.exceptions import ProvisionedThroughputExceededException

from hub.client import kinesis_client
from hub.kinesis.helpers import create_stream, stream_is_active


class Producer:
    def __init__(self, stream_name: str):
        self.stream_name = stream_name
        self.stream_name_request = stream_name + '.request'
        self.stream_name_response = stream_name + '.response'
        if not stream_is_active(self.stream_name_response):
            create_stream(self.stream_name_response)
        if not stream_is_active(self.stream_name_request):
            create_stream(self.stream_name_request)

    def produce(self, data: Dict, task_name: str) -> Dict:
        """
        Sync method, it send data through `stream_name`.request stream and
        waits for the response in `stream_name`.response
        :param data: Dictionary containing data to be transmitted
        :param task_name: Name of the task to be executed
        :return: Dictionary with the response data
        """
        # Send data
        uid = str(uuid.uuid1())
        request = dict(uuid=uid, task=task_name, headers=dict(), body=data)
        assert self.put_data(request, self.stream_name_request)

        # Wait for the response
        return self.wait_for_data(uid)

    @timeout_decorator.timeout(
        seconds=15, timeout_exception=TimeoutError, use_signals=False
    )
    def wait_for_data(self, uid: str) -> Dict:
        # Get info from the stream
        stream_info = kinesis_client.describe_stream(
            StreamName=self.stream_name_response
        )
        shard_id = stream_info['StreamDescription']['Shards'][0]['ShardId']

        # Start iterator
        shard_iterator = kinesis_client.get_shard_iterator(
            StreamName=self.stream_name_response,
            ShardId=shard_id,
            ShardIteratorType='TRIM_HORIZON',
        )
        next_iterator = shard_iterator['ShardIterator']

        while True:
            try:
                response = kinesis_client.get_records(
                    ShardIterator=next_iterator, Limit=1
                )

                records = response['Records']

                if records:
                    data = json.loads(records[0].get("Data").decode())
                    if data['uuid'] == uid:
                        return data['body']
            except ProvisionedThroughputExceededException:
                time.sleep(1)

    @staticmethod
    def put_data(data: object, stream_name: str) -> bool:
        input_data = json.dumps(data)
        partition_key = '{}-{}'.format(
            stream_name,
            str(datetime.now().isoformat() + 'Z').replace(' ', '-'),
        )

        kinesis_client.put_record(
            StreamName=stream_name, Data=input_data, PartitionKey=partition_key
        )

        return True
