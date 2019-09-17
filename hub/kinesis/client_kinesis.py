import os

import boto3

ACCESS_KEY = os.environ['ACCESS_KEY']
SECRET_KEY = os.environ['SECRET_KEY']
REGION_NAME = os.environ['AWS_DEFAULT_REGION']

client = boto3.client('kinesis', region_name=REGION_NAME,
                      aws_access_key_id=ACCESS_KEY,
                      aws_secret_access_key=SECRET_KEY)
