import datetime as dt
import json
import logging
import time
import uuid
from typing import Dict

import timeout_decorator

from hub.client import kinesis_client as client
from hub.kinesis.helpers import create_stream, dict_to_json, stream_is_active


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
        datetime = dt.datetime.utcnow()
        assert self.put_data(request, self.stream_name_request)

        # Wait for the response
        return self.wait_for_data(uid, datetime)

    @timeout_decorator.timeout(
        seconds=15, timeout_exception=TimeoutError, use_signals=False
    )
    def wait_for_data(self, uid: str, datetime_insert: dt.datetime) -> Dict:
        # Get info from the stream
        stream_info = client.describe_stream(
            StreamName=self.stream_name_response
        )
        shard_id = stream_info['StreamDescription']['Shards'][0]['ShardId']

        # Start iterator
        shard_iterator = client.get_shard_iterator(
            StreamName=self.stream_name_response,
            ShardId=shard_id,
            ShardIteratorType='AT_TIMESTAMP',
            Timestamp=datetime_insert,
        )
        next_iterator = shard_iterator['ShardIterator']

        while True:
            try:
                response = client.get_records(ShardIterator=next_iterator)

                records = response['Records']

                if records:
                    for record in records:
                        data = json.loads(record.get("Data").decode())
                        if data and data['uuid'] == uid:
                            logging.info(f'Producer: {str(data)}')
                            return data['body']

                next_iterator = response['NextShardIterator']
            except client.exceptions.ProvisionedThroughputExceededException:
                time.sleep(1)

    @staticmethod
    def put_data(data: dict, stream_name: str) -> bool:
        logging.info(f'PutData: {str(data)}')
        input_data = dict_to_json(data)
        partition_key = '{}-{}'.format(
            stream_name,
            str(dt.datetime.now().isoformat() + 'Z').replace(' ', '-'),
        )

        client.put_record(
            StreamName=stream_name, Data=input_data, PartitionKey=partition_key
        )

        return True
