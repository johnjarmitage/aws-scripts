"""
python 3.7
script to create two EC2s, 2 subnets, 1 gateway, add html, and load balance
John Armitage
"""

import re
import json
import boto3


def create2EC2(myip):

    client = boto3.client('ec2')
    ec2 = boto3.resource('ec2')

    # create vpc network
    vpc = ec2.create_vpc(CidrBlock='172.168.0.0/16')
    print(json.dumps(vpc, indent=4, sort_keys=True, default=str))
    vpc.create_tags(Tags=[{"Key": "Name", "Value": "vpc_simplon"}])
    vpc.wait_until_available()

    # create subnets in eu-west-1a
    subneta = [None] * 2
    j = 0
    for i in range(1, 4, 2):
        cidr = '172.168.' + str(i) + '.0/24'
        subneta[j] = vpc.create_subnet(
            AvailabilityZone='eu-west-1a',
            CidrBlock=cidr
        )
        j += 1

    # create subnets in eu-west-1b
    subnetb = [None] * 2
    j = 0
    for i in range(2, 5, 2):
        cidr = '172.168.' + str(i) + '.0/24'
        subnetb[j] = vpc.create_subnet(
            AvailabilityZone='eu-west-1b',
            CidrBlock=cidr
        )
        j += 1

    # create an internet gateway and attach it to VPC
    internetgateway = ec2.create_internet_gateway()
    vpc.attach_internet_gateway(InternetGatewayId=internetgateway.id)

    # create a route table and a public route
    routetable = vpc.create_route_table()
    routetable.create_route(DestinationCidrBlock='0.0.0.0/0', GatewayId=internetgateway.id)
    for j in range(2):
        routetable.associate_with_subnet(SubnetId=subneta[j].id)
        routetable.associate_with_subnet(SubnetId=subnetb[j].id)

    # create security group, SSH (22) and HTTP (80)
    securitygroup = ec2.create_security_group(
        GroupName='SSH-HTTP',
        Description='allow SSH traffic and HTTP',
        VpcId=vpc.id)
    securitygroup.authorize_ingress(
        CidrIp=myip,
        IpProtocol='tcp',
        FromPort=22,
        ToPort=22)
    securitygroup.authorize_ingress(
        CidrIp='0.0.0.0/0',
        IpProtocol='tcp',
        FromPort=80,
        ToPort=80)

    # create ssh key pairs
    # create a file to store the key locally
    outfile = open('ec2-keypair.pem', 'w')

    # call the boto ec2 function to create a key pair
    key_pair = ec2.create_key_pair(KeyName='ec2-keypair')

    # capture the key and store it in a file
    KeyPairOut = str(key_pair.key_material)
    outfile.write(KeyPairOut)
    outfile.close()

    # user data for EC2 instances

    user_data_script = """#!/bin/bash
# update
yum update -y
# install httpd and activate
yum install -y httpd
systemctl start httpd
systemctl enable httpd
# chown for www directory
usermod -a -G apache ec2-user
chown -R ec2-user:apache /var/www
chmod 2775 /var/www
find /var/www -type d -exec chmod 2775 {} \;
find /var/www -type f -exec chmod 0664 {} \;
# put instance id in a file
curl http://169.254.169.254/latest/meta-data/instance-id > /var/www/html/index.html
"""

    # create first EC2 instance
    # Create a linux instance in subnet A
    instanceA = ec2.create_instances(
        ImageId='ami-040ba9174949f6de4',
        InstanceType='t2.micro',
        MaxCount=1,
        MinCount=1,
        NetworkInterfaces=[{
            'SubnetId': subneta[0].id,
            'DeviceIndex': 0,
            'AssociatePublicIpAddress': True,
            'Groups': [securitygroup.group_id]
            }],
        UserData=user_data_script,
        KeyName='ec2-keypair')
    print(json.dumps(instanceA, indent=4, sort_keys=True, default=str))
    m = re.search("id='(.+?)'", json.dumps(instanceA, indent=4, sort_keys=True, default=str))
    ec2aid = m.group(1)
    print(ec2aid)  # is there a better way of getting the instance id?

    # Create a linux instance in subnet B
    instanceB = ec2.create_instances(
        ImageId='ami-040ba9174949f6de4',
        InstanceType='t2.micro',
        MaxCount=1,
        MinCount=1,
        NetworkInterfaces=[{
            'SubnetId': subnetb[0].id,
            'DeviceIndex': 0,
            'AssociatePublicIpAddress': True,
            'Groups': [securitygroup.group_id]
            }],
        UserData=user_data_script,
        KeyName='ec2-keypair')
    print(json.dumps(instanceB, indent=4, sort_keys=True, default=str))
    m = re.search("id='(.+?)'", json.dumps(instanceB, indent=4, sort_keys=True, default=str))
    ec2bid = m.group(1)
    print(ec2bid)

    # create load balancer
    elbname = 'newbalancer'
    elb = boto3.client('elb')
    response = elb.create_load_balancer(
        Listeners=[
            {
                'InstancePort': 80,
                'InstanceProtocol': 'HTTP',
                'LoadBalancerPort': 80,
                'Protocol': 'HTTP',
            },
        ],
        LoadBalancerName=elbname,
        SecurityGroups=[securitygroup.group_id],
        Subnets=[
            subneta[0].id,
            subnetb[0].id,
        ],
    )
    print(json.dumps(response, indent=4, sort_keys=True, default=str))

    # register instance with ELB
    response = elb.register_instances_with_load_balancer(
        LoadBalancerName=elbname,
        Instances=[
            {
                'InstanceId': ec2aid
            },
            {
                'InstanceId': ec2bid
            },
        ]
    )
    print(json.dumps(response, indent=4, sort_keys=True, default=str))


if __name__ == '__main__':

    myip = '78.192.156.95' + '/32'  # input my IP address for SSH
    create2EC2(myip)
