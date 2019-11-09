import json
import logging
import os
import time
from datetime import datetime, timedelta
from typing import Callable

from botocore.exceptions import (
    ClientError,
    ConnectionClosedError,
    ConnectTimeoutError,
    ReadTimeoutError,
)

from hub.client import kinesis_client as client
from hub.kinesis.helpers import create_stream, stream_is_active
from hub.kinesis.producer import Producer

KINESIS_TIME_SLEEP = float(os.getenv('KINESIS_TIME_SLEEP', '.3'))


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
        stream_info = client.describe_stream(
            StreamName=self.stream_name_request
        )
        shard_id = stream_info['StreamDescription']['Shards'][0]['ShardId']
        shard_iterator = client.get_shard_iterator(
            StreamName=self.stream_name_request,
            ShardId=shard_id,
            ShardIteratorType='AT_TIMESTAMP',
            Timestamp=datetime.now() - timedelta(seconds=15),
        )

        next_iterator = shard_iterator['ShardIterator']

        index = 0
        while not self.tries or index < self.tries:
            try:
                response = client.get_records(ShardIterator=next_iterator)
                records = response['Records']
                if records:
                    for record in records:
                        data = json.loads(record.get("Data").decode())
                        logging.info(f'Listener: {str(data)}')
                        resp = self.process_func(data)
                        if resp:
                            Producer.put_data(resp, self.stream_name_response)

                next_iterator = response['NextShardIterator']
                if self.tries is not None:
                    index += 1
            except (
                client.exceptions.ProvisionedThroughputExceededException,
                ClientError,
                ConnectTimeoutError,
                ReadTimeoutError,
                ConnectionClosedError,
            ):
                pass

            except client.exceptions.ExpiredIteratorException:
                next_iterator = client.get_shard_iterator(
                    StreamName=self.stream_name_request,
                    ShardId=shard_id,
                    ShardIteratorType='AT_TIMESTAMP',
                    Timestamp=datetime.now() - timedelta(seconds=15),
                )
            time.sleep(KINESIS_TIME_SLEEP)
