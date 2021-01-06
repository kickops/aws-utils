#!/usr/bin/python
# To colelct the resource sets 
import boto3
import os
import sys
import json
import botocore 
from botocore.config import Config

hosted_zone_id="<ZONEID>"
max_records=300000

config = Config(
   retries = {
      'max_attempts': 10,
      'mode': 'standard'
   }
)

route53 = boto3.client('route53',config=config)
final_records = []
def construct_data(record_sets):
    data_set = []
    data = {}
    for item in record_sets['ResourceRecordSets']:
        if item['Type'] in ["A", "MX"]:
            data['Name'] = item["Name"]
            data['Type'] = item['Type']
            data['GeoLocation'] = item.get("GeoLocation","Null")
            data_set.append(data)
    final_records.extend(data_set)
record_sets = route53.list_resource_record_sets(HostedZoneId=hosted_zone_id, MaxItems='1000')
construct_data(record_sets)
run = 1
while 'NextRecordName' in record_sets.keys():
    next_record_name = record_sets['NextRecordName']
    print('listing next set: ' + next_record_name)
    record_sets = route53.list_resource_record_sets(HostedZoneId=hosted_zone_id, StartRecordName=next_record_name, MaxItems='1000')
    run += 1
    construct_data(record_sets)
print("Total runs", run)
print("Total elements in the list is", len(final_records))
with open("/tmp/final.json", "w") as outfile:
    json.dump(final_records, outfile)
