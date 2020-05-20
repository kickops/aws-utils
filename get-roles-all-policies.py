#!/usr/bin/python -Btt


import boto3
import os
import json

ACCESS_KEY="ASXXXXX"
SECRET_KEY="XXXXX"
SESSION_TOKEN="XXXXXXXXXXBbw=="

iam = boto3.client("iam", aws_access_key_id=ACCESS_KEY,aws_secret_access_key=SECRET_KEY,aws_session_token=SESSION_TOKEN)
list_roles = [role1,rol2,rol3,role4]

role_list = []
for role in list_roles:
    group_obj = iam
    result = {}
    result[role] = {}
    managed_policies_iterator = group_obj.list_attached_role_policies(RoleName=role)
    managed_policies = [item['PolicyName'] for item in managed_policies_iterator['AttachedPolicies']]
    if managed_policies:
        result[role]['Managed_Policies'] = managed_policies
    inline_policies = group_obj.list_role_policies(RoleName=role)['PolicyNames']
    if inline_policies:
        result[role]['Inline_Policies'] = inline_policies
    role_list.append(result)
print(role_list)

with open('/tmp/roles-with-policies.txt', 'w') as fi:
    fi.write(json.dumps(role_list, indent=4))
