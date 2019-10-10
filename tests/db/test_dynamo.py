import boto3
from moto import mock_dynamodb2

from hub.db.dynamo import KINESIS_DYNAMO_TABLE, write_to_db


@mock_dynamodb2
def test_write_to_db():
    client = boto3.client('dynamodb', region_name='us-east-2')
    transaction = "f3296986-ded8-11e9-8000-000000000000"
    # First transaction
    unique: bool = write_to_db(transaction)
    assert unique

    # Create table if not exists
    tables = client.list_tables().get("TableNames")
    assert KINESIS_DYNAMO_TABLE in tables

    # Ignore Duplicated Transaction
    unique = write_to_db(transaction)
    assert not unique
