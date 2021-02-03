#!/usr/bin/python -Btt
# Author: Kicky
# Purpose: Creates a vpc peering from one vpc(initiator) to one or more vpc's(acceptors)
# Usage: create_vpc_peering <vpc-id> <vpc-id>                      # peer one to one
# Usage: create_vpc_peering <vpc-id> <vpc-id1>,<vpc-id2>,<vpc-id3> # peer one to many
# Output: Prints the status of peering creation and the route table status
########################################################################################

import os
import sys
import boto3
import time

ec2 = boto3.client("ec2", region_name='us-east-1')
resource = boto3.resource("ec2", region_name='us-east-1')


def create_peer(source_vpc, dest_vpc, dry_run=False):
    response = ec2.create_vpc_peering_connection(DryRun=dry_run, PeerVpcId=dest_vpc, VpcId=source_vpc)
    return(response['VpcPeeringConnection']['VpcPeeringConnectionId'])
  

def accept_peering(peer_id, dry_run=False):
    response = ec2.accept_vpc_peering_connection(VpcPeeringConnectionId=peer_id, DryRun=dry_run)
    return(response['VpcPeeringConnection']['VpcPeeringConnectionId'])


def is_active(peer_id):
    vpc_peering_connection = resource.VpcPeeringConnection(peer_id)
    status = vpc_peering_connection.status['Code']
    if status == "active":
       print(peer_id, "Peering is successfull! Proceeding with route table modifications")
       return True
    else:
       print(peer_id, "Peering is not active yet . Check the status in the console and fix it")
    return False


def get_vpc_cidr(vpc_id):
    vpc = resource.Vpc(vpc_id)
    return vpc.cidr_block
    

def modify_route_table(vpc_id, peer_id, cidr):
    route_table_iterator = resource.route_tables.filter(Filters=[{'Name': 'vpc-id','Values': [vpc_id]}])
    for rt in route_table_iterator:
        route = rt.create_route(DestinationCidrBlock=cidr, VpcPeeringConnectionId=peer_id)
    print("All route tables in vpc {} modified".format(vpc_id))


def modify_routes(svpc_id, dvpc_id, peer_id):
    source_cidr = get_vpc_cidr(svpc_id)
    dest_cidr = get_vpc_cidr(dvpc_id)
    modify_route_table(svpc_id, peer_id, dest_cidr)
    modify_route_table(dvpc_id, peer_id, source_cidr)


def peer(vpc1, vpc2):
    peerid = create_peer(vpc1, vpc2)
    time.sleep(2)
    accept_peering(peerid)
    time.sleep(3)
    if is_active(peerid):
       modify_routes(vpc1, vpc2, peerid)

## Get Args
args = sys.argv
if len(args) <3:
   print("Usage: create-peering source-vpc dest-vpc")
svpc = sys.argv[1]
dvpc = sys.argv[2].split(",")
for item in dvpc:
    peer(svpc, item)
