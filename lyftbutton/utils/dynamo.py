import os

import boto3

LOCAL_DYNAMO_ENDPOINT = "http://docker.for.mac.localhost:8000/"


if os.getenv("AWS_SAM_LOCAL"):
    dynamodb = boto3.resource("dynamodb", endpoint_url=LOCAL_DYNAMO_ENDPOINT)
else:
    dynamodb = boto3.resource("dynamodb")
