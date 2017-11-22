# S3 Uncompressor SAM 

[SAM](https://github.com/awslabs/serverless-application-model) application that uncompresses files uploaded to S3 bucket.

It can uncompress file:
* to the same bucket to which file was uploaded
* other bucket specified in the environment variable in the Lambda function (can be adjusted as a CloudFormation parameter) 

## Setup

#### Clone the repo

```bash
git clone https://github.com/pimlock/s3-uncompressor-sam.git
cd s3-uncompressor-sam
```

#### Install dev dependencies (make sure you are using Python3)

```bash
pip install -r dev-requirements.txt
```

#### Create Virtualenv:

```bash
virtualenv venv
source venv/bin/activate
```

#### Create CloudFormation stack

This step requires your AWS credentials to be set up:
* as `export AWS_ACCESS_KEY_ID=""; export AWS_SECRET_ACCESS_KEY=""`
* stored in `~/.aws/credentials`

Create required S3 buckets:

1. Where CloudFormation will upload Lambda code to (`CODE_DEPLOYMENT_BUCKET`)
2. Where Lambda will uncompress files to (`UNCOMPRESSOR_DESTINATION_BUCKET`). 
    * You can skip this step, in which case files will be uncompressed to the bucket where they were uploaded.

```bash
# this bucket is where the zip file with AWSLambda code will be uploaded (it's used by CloudFormation to deploy Lambda)
export CODE_DEPLOYMENT_BUCKET=my-bucket
# bucket to which contents of compressed file will be written to (if this value is empty - contents will be written to the source bucket)
export UNCOMPRESSOR_DESTINATION_BUCKET=other-bucket

# creates deployable package for CloudFormation
scripts/package.sh

# creates/updates the CloudFormation stack
scripts/deploy.sh
```

## Use

* CloudFormation creates source bucket in the following form `<aws_account_id>-<region>-uncompressor-source`
* Uploading file to that bucket will trigger Lambda, which will uncompress that file and write contents to destination bucket
    * Note: currently only zip files are supported.
    * All other files, that are not compressed, won't be processed.

&copy; 2017 Piotr Mlocek. This project is licensed under the terms of the MIT license.
