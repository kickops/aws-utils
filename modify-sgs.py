#!/usr/bin/python -Btt
# Author: Kicky
# Purpose: Fetch all security groups that is assigned to an instance and add a rule to allow port 3022 from teleport proy SG
# Usage: ./modify-sg.py
# Output: No output if everything goes well. Prints error if the SG cannot be modified
########################################################################################

import os
import sys
import boto3
import json

region="us-east-1"
ec2 = boto3.client('ec2', region_name=region)
resource = boto3.resource('ec2', region_name=region)


def get_teleport_sg_and_vpc(role):
    teleport_sgs = ec2.describe_security_groups(Filters=[{'Name': 'tag-key','Values': ['TeleportCluster',]}])
    for item in teleport_sgs['SecurityGroups']:
        if item['GroupName'].startswith("teleport-") and item['GroupName'].endswith("-{}".format(role)):
            sg_id = item['GroupId']
            vpc_id = item['VpcId']
    return sg_id, vpc_id
        

def fetch_security_groups(teleport_vpc_id):
    sg_ids = []
    vpc_ids = []
    response = ec2.describe_instances()
    instances=response['Reservations']
    for item in instances:
       ins = item['Instances']
       for instance in ins:
         secgroups = instance['SecurityGroups']
         vpc_id = instance['VpcId']
         for sg in secgroups:
             sgname = sg["GroupName"]
             sgid = sg["GroupId"]
             if vpc_id != teleport_vpc_id:
                 if vpc_id not in vpc_ids:
                    vpc_ids.append(vpc_id)
                 if sgid not in sg_ids:
                    sg_ids.append(sgid)
    return sg_ids, vpc_ids


def add_vpc_cidr_in_auth(security_group, vpc_id, cidr_range):
    try:
        cidr_description = "Allow traffic on port 3025 from the vpc ID {}".format(vpc_id)
        response = security_group.authorize_ingress(IpPermissions=[
            {
                'FromPort': 3025,
                'IpProtocol': 'tcp',
                'ToPort': 3025,
                'IpRanges': [
                {
                    'CidrIp': cidr_range,
                    'Description': cidr_description
                },
                ],},],)
    except Exception as error:
        if error.response['Error']['Code'] == "InvalidPermission.Duplicate":
           pass
        elif error.response['Error']['Code'] == "InvalidGroup.NotFound":
            print("Error: Cannot modify Security group {}. Make sure it is peered with teleport vpc".format(sgid))
        else:
            raise Exception(error)
        

def modify_auth_sg():
    teleport_auth_sg, teleport_vpc_id = get_teleport_sg_and_vpc("auth")
    security_group = resource.SecurityGroup(teleport_auth_sg)
    for vpc_id in vpc_ids:
        vpc = resource.Vpc(vpc_id)
        cidr = vpc.cidr_block
        add_vpc_cidr_in_auth(security_group, vpc_id, cidr)

def add_ingress_rule(sgid, teleport_proxy_sg, teleport_vpc_id):
    try: 
        security_group = resource.SecurityGroup(sgid)
        response = security_group.authorize_ingress(IpPermissions=[
            {
                'FromPort': 3022,
                'IpProtocol': 'tcp',
                'ToPort': 3022,
                'UserIdGroupPairs': [
                    {
                        'Description': 'Allow traffic from teleport proxy security group',
                        'GroupId': teleport_proxy_sg,
                        'VpcId': teleport_vpc_id,
                    },
                ]},],)
    except Exception as error:
        if error.response['Error']['Code'] == "InvalidPermission.Duplicate":
            pass
        elif error.response['Error']['Code'] == "InvalidGroup.NotFound":
            print("Error: Cannot modify Security group {}. Make sure it is peered with teleport vpc".format(sgid))
        else:
            raise Exception(error)
         

def modify_app_sgs():
    teleport_proxy_sg, teleport_vpc_id = get_teleport_sg_and_vpc("proxy")
    global vpc_ids
    sgs, vpc_ids = fetch_security_groups(teleport_vpc_id)
    print "Security groups that are attached to instances....")
    print sgs
    for sg in sgs:
        add_ingress_rule(sg, teleport_proxy_sg, teleport_vpc_id)


def main():
    modify_app_sgs()
    modify_auth_sg()


#MAIN
main()
