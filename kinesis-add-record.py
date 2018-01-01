import boto3
import json

stream_name = 'simple-stream'
data = {'key': 'hello world! my test again!'}
partition_key = '123456'

client = boto3.client('kinesis')
response = client.put_record(
    StreamName=stream_name,
    Data=json.dumps(data).encode('utf-8'),
    PartitionKey=partition_key)
