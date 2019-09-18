from datetime import datetime, timedelta
import json

import boto3
from moto import mock_kinesis

from hub.kinesis import Listener

stream_name = 'cuenca.api_keys'
arg = (stream_name, 3)


@mock_kinesis
def test_class_listener():
    client = boto3.client('kinesis', region_name='us-east-2')
    created_at = datetime.utcnow() - timedelta(hours=2)

    client.create_stream(StreamName='cuenca.api_keys.request', ShardCount=1)

    data = {'card_hash': (
        '6f3760fceb635962f8d8047d70d475361063624370f76c61c067ff666dc593'
        '216df0ff34a49d8f1a4c2042fa307be9521b1cd5b0e967dfb039d04e52aa91'
        'fc5b'),
        'status_authorization': 'pending',
        'affiliation': '',
        'authorizer_number': '327634',
        'merchant_name': 'NETFLIX MEXICO DF 000MX',
        'amount': 5600,
        'track_data_method': 'manual',
        'created_at': created_at.isoformat() + 'Z'}

    for index in range(5):
        client.put_record(StreamName='cuenca.api_keys.request',
                          Data=json.dumps(data),
                          PartitionKey=str(index))

    def process_records(records):
        for record in records:
            data_card = json.loads(record['Data'])
            return data_card

    listener = Listener("cuenca.api_keys", process_records, 6)
    listener.run()
    return None
