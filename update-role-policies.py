#!/usr/bin/python -Btt
# Author : Kicky
# Purpose: Add or delete Iam action from inline policy or managed policy
# Usage  : Edit the add_actions, remove_actions, POLICY_NAME and ROLE_NAME
# Input  : create a file named "input-list" containing account numbers (new line seperated)
# Output : Prinst the status of the modification

import boto3
import os
import sys
import json
import gspread
from oauth2client.service_account import ServiceAccountCredentials
from termcolor import colored

""" The below parameters needs to be modifid for each account """

#################################################################
#################################################################

sts_client = boto3.client('sts')
add_actions = []
remove_actions = ['iam:PassRole']
POLICY_NAME = 'CustodianLambdaAccess'
ROLE_NAME = 'CustodianLambdaReadOnlyRole'

def get_account_number():
    sts = boto3.client("sts", **creds) 
    response = sts.get_caller_identity()
    acc_num = response['Account']
    return acc_num


def get_account_name():
    alias = iam.list_account_aliases()['AccountAliases'][0]
    return alias


def cross_accounts_check():
    with open('input-list') as acc_num:
        aws_accounts  = [line.rstrip() for line in acc_num]
    for account in aws_accounts:
        print(colored("=====================================================================", 'yellow'))
        print(colored(account,'yellow'))
        global iam
        global resource
        global creds
        creds = get_sts_iam_object(sts_client, account, "iam")
        resource = boto3.resource("iam", **creds)
        iam = resource.meta.client
        main(account)


def construct_account_dict():
    global global_account_dict
    global_account_dict = {}
    with open('account-num-map.txt') as fi:
        all_lines = fi.read().splitlines()
    lines = [line for line in all_lines if line]
    for line in lines:
        data = line.split(':')
        number = data[0]
        account = data[1]
        global_account_dict[number] = account


def get_sts_iam_object(sts_client, account_id, service):
    creds = {}
    role_arn = 'arn:aws:iam::%s:role/%s' % (account_id, "fusion_app")
    role_session_name = 'pullCreds'
    try:
        assumed_role_object = sts_client.assume_role(
            RoleArn=role_arn, RoleSessionName=role_session_name)
        credentials = assumed_role_object['Credentials']
        creds['aws_access_key_id'] = credentials['AccessKeyId']
        creds['aws_secret_access_key'] = credentials['SecretAccessKey']
        creds['aws_session_token'] = credentials['SessionToken']
    except Exception as err:
        print("Unable to assume role in {}".format(account_id))
        print(err)
    return creds



def call_top_level_iterator(acc_num):
    found = False
    role = ROLE_NAME
    #inline_policies = iam.list_role_policies(RoleName=role)
    #for policyname in inline_policies['PolicyNames']:
    #    if policyname == POLICY_NAME:
    #        update_inline_policy(role, policyname)
    #        found = True
    #if not found: 
    response = update_managed_policy(acc_num)



def update_managed_policy(acc_num):
    try:
       pol_arn = 'arn:aws:iam::' + acc_num + ':policy/' + POLICY_NAME
       policy = resource.Policy(pol_arn)
       if not policy:
           print("managed policy {} not found".format(POLICY_NAME))
       policyJson = policy.default_version.document
       content = policyJson['Statement'][-1]['Action']
       for add_action in add_actions:
           if add_action not in content:
               policyJson['Statement'][-1]['Action'].append(add_action)
       for remove_action in remove_actions:
           if remove_action in content:
               policyJson['Statement'][-1]['Action'].remove(remove_action)
       response = iam.create_policy_version(PolicyArn = pol_arn, PolicyDocument = json.dumps(policyJson), SetAsDefault = True)
       print("Succesfully updated the managed policy")
    except Exception as error:
        print(error)
        print("Failed in finding/updating the managed policy")


def update_inline_policy(role, policyname):
    try:
        policy = iam.get_role_policy(RoleName = role, PolicyName = policyname)
        content = policy['PolicyDocument']['Statement'][-1]['Action']
        for add_action in add_actions:
            if add_action not in content:
                policy['PolicyDocument']['Statement'][-1]['Action'].append(add_action)
        for remove_action in remove_actions:
            if remove_action in content:
                policy['PolicyDocument']['Statement'][-1]['Action'].remove(remove_action)
        response = iam.put_role_policy(RoleName=role,PolicyName=policyname,PolicyDocument=json.dumps(policy['PolicyDocument']))
        print("succesfully updated the inline policy")
    except Exception as error:
        print("Failed in updating inline policy")

def main(account):
    call_top_level_iterator(account)

##MAIN
construct_account_dict()
cross_accounts_check()


