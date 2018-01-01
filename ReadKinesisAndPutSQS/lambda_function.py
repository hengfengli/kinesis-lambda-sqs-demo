from __future__ import print_function

import base64
import boto3
import json


def process_records(records, queue_name):
    sqs = boto3.resource('sqs')
    queue = sqs.get_queue_by_name(QueueName=queue_name)
    data = []
    for record in records:
        try:
            decoded_payload = json.loads(record)
            data.append(decoded_payload)
            if len(json.dumps(data)) >= 262000:
                data.pop()
                queue.send_message(MessageBody=json.dumps(data))
                data = [decoded_payload]
        except Exception as e:
            print('Error: {}'.format(e))
            print('Current data: {}'.format(record))
    if data:
        queue.send_message(MessageBody=json.dumps(data))


def lambda_handler(event, context):
    if not event.get('async'):
        invoke_self_async(event, context)
        return

    process_records(event['records'], "simple-queue")


def invoke_self_async(event, context):
    """
    Have the Lambda invoke itself asynchronously, passing the same event it received originally,
    and tagging the event as 'async' so it's actually processed
    """
    data = []
    event_template = {'async': True, 'records': []}

    def send_data(data_to_send):
        event_to_send = event_template.copy()
        event_to_send['records'] = data_to_send
        called_function = context.invoked_function_arn
        boto3.client('lambda').invoke(
            FunctionName=called_function,
            InvocationType='Event',
            Payload=json.dumps(event_to_send).encode('utf-8'))

    for record in event['Records']:
        # Kinesis data is base64 encoded so decode here
        payload = base64.b64decode(record['kinesis']['data']).decode('utf-8')
        data.append(payload)
        if len(json.dumps(data)) >= 130000:
            data.pop()
            send_data(data)
            data = [payload]
    if data:
        send_data(data)
