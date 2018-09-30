#!/bin/bash

aws dynamodb create-table --table-name LyftCredential --attribute-definitions AttributeName=serial_number,AttributeType=S --key-schema AttributeName=serial_number,KeyType=HASH --provisioned-throughput ReadCapacityUnits=5,WriteCapacityUnits=5 --endpoint http://localhost:8000

aws dynamodb create-table --table-name Token --attribute-definitions AttributeName=lyft_id,AttributeType=S --key-schema AttributeName=lyft_id,KeyType=HASH --provisioned-throughput ReadCapacityUnits=5,WriteCapacityUnits=5 --endpoint http://localhost:8000
