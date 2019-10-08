import boto3
import pytest
from moto import mock_dynamodb2

from hub.db.dynamo import KINESIS_DYNAMO_TABLE, write_to_db


@mock_dynamodb2
def test_write_to_db():
    client = boto3.client('dynamodb', region_name='us-east-2')

    client.create_table(
        TableName=KINESIS_DYNAMO_TABLE,
        KeySchema=[{'AttributeName': 'uuid', 'KeyType': 'HASH'}],
        AttributeDefinitions=[
            {'AttributeName': 'uuid', 'AttributeType': 'S'},
            {'AttributeName': 'ttl', 'AttributeType': 'N'},
        ],
    )

    transaction = "f3296986-ded8-11e9-8000-000000000000"
    unique: bool = write_to_db(transaction)
    assert unique
    # Duplicated Transaction
    unique = write_to_db(transaction)
    assert not unique


@mock_dynamodb2
def test_service_not_available():
    transaction = "f3296986-ded8-11e9-8000-000000000000"
    with pytest.raises(ValueError):
        write_to_db(transaction)
