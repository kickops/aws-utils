#!/usr/bin/python -Btt
# Author: Kicky
# Purpose: Fetch all instances and get their VPC details and no of instances in each vpc
# Usage: ./get-vpc
# Output: Prints a tabular column of the vpc & number of instances
#         Also prints a vpc peering command for your ease
########################################################################################

import os
import sys
import boto3
import json


vpc_mapping={}
ec2 = boto3.client('ec2', region_name="us-east-1")

response = ec2.describe_instances()
instances=response['Reservations']
for item in instances:
   ins = item['Instances']
   for instance in ins:
     vpc_id = instance['VpcId']
     instance_id = instance['InstanceId']
     if vpc_id in vpc_mapping:
       vpc_mapping[vpc_id] += 1
     else:
       vpc_mapping[vpc_id] = 1

print ("{:<25} {:<10}".format('VPC-ID', 'No of Instances')) 
print("-" * 42) 
for key, value in vpc_mapping.iteritems(): 
    print ("{:<25} {:<10}".format(key, value)) 
print("-" * 42) 

keys = vpc_mapping.iterkeys()
keys_str = ",".join(keys)
print("You can use the following command to peer all vpc's")
print("`create-peering <teleport-vpcid> {}`".format(keys_str))
