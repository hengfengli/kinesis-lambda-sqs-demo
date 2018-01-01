# Introduction

This demo is inspired by an article [Implementing real-time analytics using AWS Kinesis & Lambda](https://engineering.dubsmash.com/implementing-real-time-analytics-using-aws-kinesis-lambda-1ea56f10e473). 

I mainly use [troposphere](https://github.com/cloudtools/troposphere) to create AWS resources. Basically, troposphere is a python library to generate CloudFormation template file. The major advantage of using troposphere is that you can programmatically manage your template generation to avoid writing the same template code everywhere. Also, it can help you detect some simple errors by checking. 

CloudFormation is a really powerful tool to provision AWS resources automatically. It has all tiny details when creating a stack and also it will clean up everything when deleting a stack. 

The idea of this demo is simple, in which lambda function reads records from kinesis stream and put records into SQS in batch. 

# Deploy Steps

## Zip your code and dependencies and upload to S3

When creating a lambda function, you need to upload the code and dependencies. 

```bash
# create the virtual environment
$ cd ReadKinesisAndPutSQS
$ virtualenv -p python3 .venv
# activate virtualenv (I use fish shell)
$ . ./.venv/bin/activate.fish
# install the dependencies
$ pip install boto3
# enter the library directory (important)
$ cd .venv/lib/python3.6/site-packages/
# all dependencies need to be added on the root level
$ zip -r9 ~/ReadKinesisAndPutSQS.zip *
# move back to your project root directory
$ cd ReadKinesisAndPutSQS
# add the code to the zip file
$ zip -g ~/ReadKinesisAndPutSQS.zip lambda_function.py
```

Then, you can upload the zip file to a S3 bucket. S3 bucket's Versioning is enabled for the convience to update lambda function in the future. 

## Create the stack

```bash
$ pip install troposphere
$ python create-stack.py > template.json
```

Now, you can go to AWS CloudFormation and create a stack based on the template json file. 

## Test

```bash
$ pip install boto3
$ python kinesis-add-record.py
```

You should see a new record in SQS. For debugging, you can check logs in CloudWatch. 
