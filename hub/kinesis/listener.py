import time

from hub.kinesis.client_kinesis import client
from hub.kinesis.initialize_stream import check_status_stream, create_stream
from hub.kinesis.responser import put_response


class Listener:
    def __init__(self, stream_name: str, process_records, tries=None):
        self.stream_name = stream_name
        self.stream_name_request = stream_name + '.request'
        self.stream_name_response = stream_name + '.response'
        self.process_records = process_records
        self.tries = tries
        if check_status_stream(self.stream_name_response) != 'ACTIVE':
            create_stream(self.stream_name_response)
        if check_status_stream(self.stream_name_request) != 'ACTIVE':
            create_stream(self.stream_name_request)

    def run(self):
        stream_info = client.describe_stream(
            StreamName=self.stream_name + '.request'
        )
        shard_id = stream_info['StreamDescription']['Shards'][0]['ShardId']
        shard_iterator = client.get_shard_iterator(
            StreamName=self.stream_name + '.request',
            ShardId=shard_id,
            ShardIteratorType='TRIM_HORIZON',
        )

        next_iterator = shard_iterator['ShardIterator']

        index = 0
        while not self.tries or index < self.tries:
            try:
                response = client.get_records(
                    ShardIterator=next_iterator, Limit=1
                )

                records = response['Records']

                if records:
                    resp = self.process_records(records[0])
                    put_response(resp, self.stream_name_response)

                next_iterator = response['NextShardIterator']
                if self.tries is not None:
                    index += 1
            except client.exceptions.ProvisionedThroughputExceededException:
                time.sleep(1)
