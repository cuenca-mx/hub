from datetime import datetime, timedelta
import json

import boto3
from moto import mock_kinesis

from hub.kinesis.listener import Listener
from hub.workers.class_worker import Worker

stream_name_request = "my_stream"
stream_name_response = 'my_stream_response'
arg = (stream_name_request, 3)


def process_records(records):
    for record in records:
        data_card = json.loads(record['Data'])
        return data_card


@mock_kinesis
def test_class_listener():
    client = boto3.client('kinesis', region_name='us-east-2')
    created_at = datetime.utcnow() - timedelta(hours=2)

    client.create_stream(StreamName=stream_name_request, ShardCount=1)

    data = {'card_hash': (
        '6f3760fceb635962f8d8047d70d475361063624370f76c61c067ff666dc593'
        '216df0ff34a49d8f1a4c2042fa307be9521b1cd5b0e967dfb039d04e52aa91'
        'fc5b'),
        'status_authorization': 'pending',
        'affiliation': '',
        'authorizer_number': '327634',
        'merchant_name':
            'NETFLIX               MEXICO DF    000MX',
        'amount': 5600,
        'track_data_method': 'manual',
        'created_at': created_at.isoformat() + 'Z'}

    for index in range(5):
        client.put_record(StreamName=stream_name_request,
                          Data=json.dumps(data),
                          PartitionKey=str(index))

    consumer = Listener(stream_name_request, stream_name_response,
                        process_records, 3)

    resp = consumer.run()

    worker = Worker(resp)
    worker.start()
    assert resp is None
