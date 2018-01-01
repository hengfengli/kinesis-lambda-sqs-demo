from troposphere.constants import NUMBER
from troposphere import Output, Parameter, Ref, Template, GetAtt
from troposphere import Join
import troposphere.kinesis as kinesis
from troposphere.sqs import Queue, QueuePolicy
from troposphere.awslambda import Function, Code, MEMORY_VALUES, EventSourceMapping
from troposphere.iam import Role, Policy, PolicyType

template = Template()

template.add_description("AWS CloudFormation Template: "
                         "Kinesis Stream + Lambda + SQS.")

s3_bucket = template.add_parameter(
    Parameter(
        "CodeS3Bucket", Description="Name of code bucket", Type="String"))

s3_key = template.add_parameter(
    Parameter("CodeS3Key", Description="Name of code zip file", Type="String"))

s3_object_version_id = template.add_parameter(
    Parameter(
        "CodeS3ObjectVersionID",
        Description="Version ID of zip file",
        Type="String"))

memory_size = template.add_parameter(
    Parameter(
        'LambdaMemorySize',
        Type=NUMBER,
        Description='Amount of memory to allocate to the Lambda Function',
        Default='128',
        AllowedValues=MEMORY_VALUES))

timeout = template.add_parameter(
    Parameter(
        'LambdaTimeout',
        Type=NUMBER,
        Description='Timeout in seconds for the Lambda function',
        Default='60'))

kinesis_param = template.add_parameter(
    Parameter(
        "CapturedDataKinesisStreamName",
        Description="Name of Captured Data Kinesis Stream",
        Default="simple-stream",
        Type="String"))

sqs_param = template.add_parameter(
    Parameter(
        "SQSQueueName",
        Description="Name of Captured Data SQS",
        Default="simple-queue",
        Type="String"))

sqsqueue = template.add_resource(
    Queue("CapturedDataQueue", QueueName=Ref("SQSQueueName")))

template.add_resource(
    QueuePolicy(
        "CapturedDataQueuePolicy",
        Queues=[Ref(sqsqueue)],
        PolicyDocument={
            "Version":
            "2012-10-17",
            "Statement": [{
                "Sid": "LambdaWriteToQueue",
                "Effect": "Allow",
                "Principal": {
                    "AWS": GetAtt("LambdaExecutionRole", "Arn")
                },
                "Action": "SQS:*",
                "Resource": GetAtt(sqsqueue, "Arn")
            }]
        }))

kinesis_stream = template.add_resource(
    kinesis.Stream(
        "CapturedDataKinesisStream",
        Name=Ref(kinesis_param),
        ShardCount=1,
        RetentionPeriodHours=24))

kinesis_consumer = template.add_resource(
    Function(
        "ReadKinesisAndPutQueueFunction",
        Code=Code(
            S3Bucket=Ref(s3_bucket),
            S3Key=Ref(s3_key),
            S3ObjectVersion=Ref(s3_object_version_id)),
        Handler="lambda_function.lambda_handler",
        Role=GetAtt("LambdaExecutionRole", "Arn"),
        Runtime="python3.6",
        MemorySize=Ref(memory_size),
        Timeout=Ref(timeout)))

lambda_execution_role = template.add_resource(
    Role(
        "LambdaExecutionRole",
        Path="/",
        Policies=[
            Policy(
                PolicyName="root",
                PolicyDocument={
                    "Version":
                    "2012-10-17",
                    "Statement": [
                        {
                            "Action": ["logs:*"],
                            "Resource": "arn:aws:logs:*:*:*",
                            "Effect": "Allow"
                        },
                    ]
                }),
        ],
        AssumeRolePolicyDocument={
            "Version":
            "2012-10-17",
            "Statement": [{
                "Action": ["sts:AssumeRole"],
                "Effect": "Allow",
                "Principal": {
                    "Service": ["lambda.amazonaws.com"]
                }
            }]
        },
        ManagedPolicyArns=[
            "arn:aws:iam::aws:policy/AmazonKinesisReadOnlyAccess",
            "arn:aws:iam::aws:policy/service-role/AWSLambdaRole"
        ]))

template.add_resource(
    EventSourceMapping(
        "LambdaKinesisTrigger",
        BatchSize=100,
        Enabled=True,
        EventSourceArn=GetAtt(kinesis_stream, "Arn"),
        FunctionName=GetAtt(kinesis_consumer, "Arn"),
        StartingPosition="TRIM_HORIZON"))

template.add_output([
    Output(
        "CapturedDataStreamName",
        Description="CapturedDataKinesisStreamName",
        Value=Ref(kinesis_stream), ),
])

print(template.to_json())
