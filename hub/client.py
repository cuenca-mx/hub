import os

import boto3

REGION_NAME = os.environ['REGION_NAME']

kinesis_client = boto3.client('kinesis', region_name=REGION_NAME)

dynamo_client = boto3.client('dynamodb', region_name=REGION_NAME)
