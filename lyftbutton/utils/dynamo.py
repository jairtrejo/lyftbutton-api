import os

import boto3


DYNAMO_ENDPOINT = os.environ.get('DYNAMO_ENDPOINT')


if DYNAMO_ENDPOINT:
    print('Using custom endpoint: %s' % DYNAMO_ENDPOINT)
    dynamodb = boto3.resource('dynamodb', endpoint_url=DYNAMO_ENDPOINT)
else:
    dynamodb = boto3.resource('dynamodb')
