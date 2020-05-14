#!/usr/bin/env python -Btt
## Common utilities for aws IAM service
##Author: Karthik.S

import boto3
import sys



def get_sts_iam_object(sts_client, account_id):
    aws_role_name = "ad_sync"
    role_arn = 'arn:aws:iam::%s:role/%s' % (account_id, aws_role_name)
    role_session_name = '%s_aws_reaper' % account_id
    assumed_role_object = sts_client.assume_role(
            RoleArn=role_arn, RoleSessionName=role_session_name)
    credentials = assumed_role_object['Credentials']
    iam = boto3.client(
          'iam',
          aws_access_key_id=credentials['AccessKeyId'],
          aws_secret_access_key=credentials['SecretAccessKey'],
          aws_session_token=credentials['SessionToken'],
        )
    return iam


def add_user_to_group(user, group):
    """ Adds an IAM user to an IAM group """

    user_exist = check_if_user_exists(user)
    if not user_exist:
        create_iam_user(user)
    client = boto3.client("iam")
    response = client.add_user_to_group(GroupName=group, UserName=user)
    return response["ResponseMetadata"]


def create_iam_user(username):
    """ Creates a new IAM user """

    iam = boto3.client("iam")
    response = iam.create_user(UserName=username)
    return response["ResponseMetadata"]


def create_iam_group(groupname):
    """ Creates a new IAM group """

    iam = boto3.client("iam")
    try:
        response = iam.create_group(GroupName=groupname)
        return response["ResponseMetadata"]
    except Exception as e:
        if e.response['Error']['Code'] == 'EntityAlreadyExists':
           return True 


def check_if_user_exists(username):
    """ Checks if an IAM user exists in the account """

    found = False
    iam = boto3.client("iam")
    try:
        user_obj = iam.get_user(UserName=username)
        found = True
    except Exception as e:
        if e.response['Error']['Code'] == 'NoSuchEntity':
            found = False
    return found


def add_users_to_group(group, user_list):
    """ Adds list of users to an IAM group """

    client = boto3.client("iam")
    for user in user_list:
        user_exist = check_if_user_exists(user)
        if not user_exist:
            create_iam_user(user)
        response = client.add_user_to_group(GroupName=group, UserName=user)


def remove_user_from_group(group, user):
    """ Remove a user from an IAM group """

    iam = boto3.client("iam")
    response = iam.remove_user_from_group(GroupName=group, UserName=user)
    return response["ResponseMetadata"]


def remove_users_from_group(group, user_list):
    """ Removes a list of user from IAM group """

    iam = boto3.client("iam")
    for user in user_list:
        response = iam.remove_user_from_group(GroupName=group, UserName=user)


def fetch_group_members(group):
    """ Returns a list of members part of an IAM group """

    client = boto3.client("iam")
    group_obj = client.get_group(GroupName=group)
    members = [user['UserName'] for user in group_obj['Users']]
    return sorted(members)


def check_user_on_group(user, group):
    """ Returns boolean value based on the presence """

    client = boto3.client("iam")
    group_obj = client.get_group(GroupName=group)
    found = False
    for item in group_obj['Users']:
        if item['UserName'] == user:
            found = True
    return found


def check_user_groups(user):
    """ Returns a sorted list of all the groups the user is member of """

    client = boto3.client("iam")
    user_obj = client.list_groups_for_user(UserName=user)
    groups = [group['GroupName'] for group in user_obj['Groups']]
    return sorted(groups)


def delete_iam_group(group):
    """ Deletes an IAM group """
    client = boto3.client("iam")
    response = client.delete_group(GroupName=group)
    return response["ResponseMetadata"]


def delete_iam_user(user):
    """ Deletes an IAM user """
    client = boto3.client("iam")
    response = client.delete_user(UserName=user)
    return response["ResponseMetadata"]


