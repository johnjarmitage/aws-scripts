"""
python 3.7
create a vpc functions
John Armitage
"""

import re
import json
import boto3

ec2_client = boto3.client('ec2')
ec2_resource = boto3.resource('ec2')


def createvpc(vpcname, vpccidr):

    # test if vpc exists
    response = ec2_client.describe_vpcs(
        Filters=[
            {
                'Name': 'tag:Name',
                'Values': [vpcname]
            },
            {
                'Name': 'cidr-block-association.cidr-block',
                'Values': [vpccidr]
            },
        ]
    )
    resp = response['Vpcs']
    if resp:
        print("VPC exists:")
        print(json.dumps(resp, indent=4, sort_keys=True, default=str))
    else:
        # create vpc network
        vpc = ec2_resource.create_vpc(CidrBlock=vpccidr)
        print(json.dumps(vpc, indent=4, sort_keys=True, default=str))
        vpc.create_tags(
            Tags=[
                {
                    "Key": "Name",
                    "Value": vpcname
                }
            ]
        )
        vpc.wait_until_available()

        # check create target-group returned successfully
        if vpc:
            print("Successfully created VPC")
        else:
            print("Create target group failed")
            exit()


if __name__ == '__main__':
    my_vpcname = 'vpc-simplon'
    my_vpccidr = '172.168.0.0/16'
    createvpc(my_vpcname, my_vpccidr)
