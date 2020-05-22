import boto3
import os
import json

""" The below parameters needs to be modifid for each account """

#################################################################

#AWS_ACCESS_KEY_ID=""
#AWS_SECRET_ACCESS_KEY=""
#AWS_SESSION_TOKEN=""

#################################################################

role_name = "<role-name>"
policy_name = "<policy-name>"

iam = boto3.client("iam", aws_access_key_id=AWS_ACCESS_KEY_ID,aws_secret_access_key=AWS_SECRET_ACCESS_KEY,aws_session_token=AWS_SESSION_TOKEN)


def add_inline_policies(client):
    with open('/tmp/inline-policy.json', 'r') as readfile:
        policy = json.load(readfile)
    document = policy[policy_name]
    response = client.put_role_policy(RoleName=role_name,PolicyName=policy_name,PolicyDocument=json.dumps(document))
    print(response['ResponseMetadata']['HTTPStatusCode'])


##main
add_inline_policies(iam)
