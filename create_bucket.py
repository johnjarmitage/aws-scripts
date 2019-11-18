"""
Python 3.7
test script to create a bucket SIMPLON/DEV
John Armitage 18/11/2019
"""

import boto3

client = boto3.client('s3')

response = client.create_bucket(
    Bucket='simplon-gekko-armitage-18112019',
    CreateBucketConfiguration={
        'LocationConstraint': 'eu-west-1'
    },
)
print(json.dumps(response, indent=4, sort_keys=True, default=str))