import boto3
import os
import json

ACCESS_KEY="ASIXXXXXXXX4T"
SECRET_KEY="YfxXXXXXXXX""
SESSION_TOKEN="xxxxxxxxxxxxxxXXXXXXXXxxx"

iam = boto3.resource("iam", aws_access_key_id=ACCESS_KEY,aws_secret_access_key=SECRET_KEY,aws_session_token=SESSION_TOKEN)
inline_policies = {role1: inlinepolicy1, role2:inlinepolicy2}
result = {}
for role,policy in inline_policies.items():
    role_policy = iam.RolePolicy(role,policy)
    result[policy] = role_policy.policy_document
print(result)
with open('/tmp/inline-policy.json', 'w') as fi:
    fi.write(json.dumps(result, indent=2))

