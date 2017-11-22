#!/usr/bin/env bash

aws cloudformation deploy \
    --template-file ./packaged-template.yaml \
    --stack-name S3UncompressLambdaStack \
    --capabilities CAPABILITY_IAM \
    --parameter-overrides destinationBucket=$UNCOMPRESSOR_DESTINATION_BUCKET