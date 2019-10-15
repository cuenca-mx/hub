import json
import time
from typing import Callable

from boto.kinesis.exceptions import (
    ExpiredIteratorException,
    ProvisionedThroughputExceededException,
)

from hub.client import kinesis_client
from hub.kinesis.helpers import create_stream, stream_is_active
from hub.kinesis.producer import Producer


class Listener:
    def __init__(
        self, stream_name: str, process_func: Callable, tries: int = None
    ):
        self.stream_name = stream_name
        self.stream_name_request = stream_name + '.request'
        self.stream_name_response = stream_name + '.response'
        self.process_func = process_func
        self.tries = tries
        if not stream_is_active(self.stream_name_response):
            create_stream(self.stream_name_response)
        if not stream_is_active(self.stream_name_request):
            create_stream(self.stream_name_request)

    def run(self):
        stream_info = kinesis_client.describe_stream(
            StreamName=self.stream_name_request
        )
        shard_id = stream_info['StreamDescription']['Shards'][0]['ShardId']
        shard_iterator = kinesis_client.get_shard_iterator(
            StreamName=self.stream_name_request,
            ShardId=shard_id,
            ShardIteratorType='TRIM_HORIZON',
        )

        next_iterator = shard_iterator['ShardIterator']

        index = 0
        while not self.tries or index < self.tries:
            try:
                response = kinesis_client.get_records(
                    ShardIterator=next_iterator, Limit=1
                )

                records = response['Records']

                if records:
                    data = json.loads(records[0].get("Data").decode())
                    resp = self.process_func(data)
                    Producer.put_data(resp, self.stream_name_response)

                next_iterator = response['NextShardIterator']
                if self.tries is not None:
                    index += 1
            except ProvisionedThroughputExceededException:
                time.sleep(1)
            except ExpiredIteratorException:
                next_iterator = kinesis_client.get_shard_iterator(
                    StreamName=self.stream_name_request,
                    ShardId=shard_id,
                    ShardIteratorType='TRIM_HORIZON',
                )
