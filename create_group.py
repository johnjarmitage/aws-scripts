"""
Python 3.7
test script
John Armitage 18/11/2019
"""

import boto3
import json

# ec2 = boto3.client('ec2')
# response = ec2.describe_instances()
# print(json.dumps(response, sort_keys=True, indent=4))

grname = 'simplon2'

client = boto3.client('iam')
response = client.create_group(
    GroupName=grname,
)
print(json.dumps(response, indent=4, sort_keys=True, default=str))

PolicyArn = 'arn:aws:iam::aws:policy/AmazonS3ReadOnlyAccess'

iam = boto3.resource('iam')
policy = iam.Policy(PolicyArn)
response = policy.attach_group(
    GroupName=grname,
)
print(json.dumps(response, indent=4, sort_keys=True, default=str))
