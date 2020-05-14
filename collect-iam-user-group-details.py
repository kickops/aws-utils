
#!/usr/bin/env python -Btt
import boto3
import json
import yaml

client = boto3.client('iam')
users = client.list_users()
final_dict = {}
user_list = []

for key in users['Users']:
    result = {}
    Inline_Policies = []
    Managed_Policies = []
    Groups=[]

    result['userName']=key['UserName']
    List_of_Policies =  client.list_user_policies(UserName=key['UserName'])
    inline_policies = List_of_Policies['PolicyNames']
    if inline_policies:
       result['Inline_Policies']  = inline_policies

    List_of_managed_policies = client.list_attached_user_policies(UserName=key['UserName'])
    managed_policies = List_of_managed_policies['AttachedPolicies']
    man_pol = [item["PolicyName"] for item in managed_policies]
    if man_pol:
        result["Managed_Policies"] = man_pol

    List_of_Groups =  client.list_groups_for_user(UserName=key['UserName'])

    for Group in List_of_Groups['Groups']:
        Groups.append(Group['GroupName'])
    result['Groups'] = Groups

    List_of_MFA_Devices = client.list_mfa_devices(UserName=key['UserName'])

    if not len(List_of_MFA_Devices['MFADevices']):
        result['isMFADeviceConfigured']=False   
    else:
        result['isMFADeviceConfigured']=True    
    user_list.append(result)
final_dict["Users"] = user_list

iam = boto3.client("iam")
groups = iam.list_groups()
list_groups = [item['GroupName'] for item in groups['Groups']]
group_list = []
for group in list_groups:
    iam = boto3.resource('iam')
    group_obj = iam.Group(group)
    result = {}
    result['groupName'] = group
    managed_policies_iterator = group_obj.attached_policies.all()
    managed_policies = [item.policy_name for item in managed_policies_iterator]
    if managed_policies:
        result['Managed_Policies'] = managed_policies
    inline_policies_iterator = group_obj.policies.all()
    inline_policies = [item.policy_name for item in inline_policies_iterator]
    if inline_policies:
        result['Inline_Policies'] = inline_policies
    user_iterator = group_obj.users.all()
    users = [item.user_name for item in user_iterator]
    if users:
        result['Users'] = users
    group_list.append(result)
final_dict['Groups'] = group_list

with open('/tmp/iam-dump.txt', 'w') as fi:
    fi.write(json.dumps(final_dict, indent=4))
