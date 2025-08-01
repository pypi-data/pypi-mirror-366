#! /bin/bash
cd ./tests/data/dynamodb_local_latest
curl -O "https://s3-us-west-2.amazonaws.com/dynamodb-local/dynamodb_local_latest.tar.gz"
tar -xvzf dynamodb_local_latest.tar.gz; rm dynamodb_local_latest.tar.gz
java -Djava.library.path=./DynamoDBLocal_lib -jar DynamoDBLocal.jar -sharedDb &
