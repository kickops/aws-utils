import boto3
import os
import json

""" The script is used to create a saml federation role with list of managed and inline policies from different files"""

#The below parameters needs to be modifid for each account
#################################################################
ACC="XXXXXXXXXXXX"
AWS_ACCESS_KEY_ID="XXXXXXX"
AWS_SECRET_ACCESS_KEY="XXXXXXXXXXXX"
AWS_SESSION_TOKEN="XXXXXXXXXXXXXXXXXXXXXXXXXXx"
#################################################################


iam = boto3.client("iam", aws_access_key_id=AWS_ACCESS_KEY_ID,aws_secret_access_key=AWS_SECRET_ACCESS_KEY,aws_session_token=AWS_SESSION_TOKEN)

custom_default_arn="arn:aws:iam::ACCOUNT:policy/"

custom_arn = custom_default_arn.replace("ACCOUNT", ACC)
managed_arn="arn:aws:iam::aws:policy/"



def create_roles():
    with open('/tmp/role-policies.json', 'r') as fi:
        role_json = json.load(fi)
    with open('/tmp/trust-role.json', 'r') as fa:
        trust_document = json.load(fa)

    for item in role_json:
       for k,v in item.items():
          resp = role_create(iam, k, json.dumps(trust_document).replace('ACCOUNT',ACC))
          add_managed_policies(iam, k, v)
          add_inline_policies(iam, k, v)
          print("role created", k)
 
def add_managed_policies(iam, rolename, role_json):
    man_pols = role_json["Managed_Policies"]
    for item in man_pols:
       if item == "Billing":
           new_arn = "arn:aws:iam::aws:policy/job-function/Billing"
       else:
           new_arn = managed_arn + item
       response = iam.attach_role_policy(RoleName=rolename,PolicyArn=new_arn)


def add_inline_policies(client, rolename, role_json):
    if "Inline_Policies" in role_json:
        inline_policy_name = role_json["Inline_Policies"][0]
        with open('/tmp/inline-policy.json', 'r') as readfile:
            policy = json.load(readfile)
        document = policy[inline_policy_name]
        response = client.put_role_policy(RoleName=rolename,PolicyName=inline_policy_name,PolicyDocument=json.dumps(document))

def role_create(client,rolename,document):
    response = client.create_role(Path='/',RoleName=rolename,AssumeRolePolicyDocument=document,
                                 Description=rolename, Tags=[{'Key': 'Owner','Value': 'Karthik'},{'Key': 'Description','Value':'Used for SSO'}])
    return response

##main
create_roles()
