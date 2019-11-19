"""
python 3.7
script to create user and give a specific policy
John Armitage
"""

import boto3
import json

username = 'simplon_other'
identity = '435606335423'
policyname = 'myEC2simplonPolicy'

# create the user simplon
client = boto3.client('iam')
response = client.create_user(UserName=username)
print(json.dumps(response, indent=4, sort_keys=True, default=str))

# add user password
iam = boto3.resource('iam')
user = iam.User(username)
login_profile = user.create_login_profile(
    Password='testing',
    PasswordResetRequired=False
)

# create the policy for the user
my_managed_policy = {
    "Version": "2012-10-17",
    "Statement": [
        {
             "Effect": "Allow",
            "Action": [
                "ec2:StartInstances",
                "ec2:StopInstances"
            ],
            "Resource": "arn:aws:ec2:*:*:instance/*"
        },
        {
            "Effect": "Allow",
            "Action": "ec2:DescribeInstances",
            "Resource": "*"
        }
    ]
}
response = client.create_policy(
  PolicyName=policyname,
  PolicyDocument=json.dumps(my_managed_policy)
)
print(json.dumps(response, indent=4, sort_keys=True, default=str))

# attach policy
PolicyArn = ("arn:aws:iam::{}:policy/{}", format(identity, policyname))
print(PolicyArn)
policy = iam.Policy(PolicyArn)
response = policy.attach_user(UserName=username)
print(json.dumps(response, indent=4, sort_keys=True, default=str))
