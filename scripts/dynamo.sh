#!/bin/bash

aws dynamodb create-table --table-name LyftCredential --attribute-definitions AttributeName=serial_number,AttributeType=S --key-schema AttributeName=serial_number,KeyType=HASH --provisioned-throughput ReadCapacityUnits=5,WriteCapacityUnits=5 --endpoint http://localhost:8000

aws dynamodb create-table --table-name Token --attribute-definitions AttributeName=lyft_id,AttributeType=S --key-schema AttributeName=lyft_id,KeyType=HASH --provisioned-throughput ReadCapacityUnits=5,WriteCapacityUnits=5 --endpoint http://localhost:8000

aws dynamodb create-table --table-name LyftButton --attribute-definitions AttributeName=serial_number,AttributeType=S AttributeName=lyft_id,AttributeType=S --key-schema AttributeName=serial_number,KeyType=HASH --global-secondary-indexes IndexName=lyft_id,KeySchema=[\{AttributeName=lyft_id,KeyType=HASH\}],Projection=\{ProjectionType=KEYS_ONLY\},ProvisionedThroughput=\{ReadCapacityUnits=5,WriteCapacityUnits=5\} --provisioned-throughput ReadCapacityUnits=5,WriteCapacityUnits=5 --endpoint http://localhost:8000
