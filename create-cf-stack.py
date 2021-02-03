#!/bin/bash
# Author: Kicky
# Purpose: create a cloudFormation stack for vpc creation. Subnet details are auto splitted from the cidr range
# Usage: ./create-vpc-stack <cidr>
# Output: displays the stack id
###############################################################################################################

stack_name="test-stack"
sub_mask=26
cidr=$1

subnet_arrays=`netcalc split $cidr $sub_mask`
read -r pub1 pub2 pub3 pub4 pri1 pri2 pri3 pri4  <<<$(echo $subnet_arrays)

progressbar() {
  local duration=${1}
    already_done() { for ((done=0; done<$elapsed; done++)); do printf "▇"; done }
    remaining() { for ((remain=$elapsed; remain<$duration; remain++)); do printf " "; done }
    percentage() { printf "| %s%%" $(( (($elapsed)*100)/($duration)*100/100 )); }
    clean_line() { printf "\r"; }

  for (( elapsed=1; elapsed<=$duration; elapsed++ )); do
      already_done; remaining; percentage
      sleep 2
      clean_line
  done
  clean_line
}


get_outputs()
{
   aws cloudformation describe-stacks --stack-name $stack_name > outputs.json
   for i in VPC VPCCIDR EIP PrivateSubnet1 PrivateSubnet2 PrivateSubnet3 PrivateSubnet4 PublicSubnet1 PublicSubnet2 PublicSubnet3 PublicSubnet4
   do
   out=`jq -c '.Stacks[0].Outputs[] | select( .OutputKey == '\"${i}\"' )'.OutputValue outputs.json`
   export $i=$out
   done
   echo "Paste the following line in the excel sheet"
   echo
   echo $VPC $VPCCIDR $EIP $PrivateSubnet1 $PrivateSubnet2 $PrivateSubnet3 $PrivateSubnet4 $PublicSubnet1 $PublicSubnet2 $PublicSubnet3 $PublicSubnet4 | tr -d '"'
}

describe_stack()
{
   status=`aws cloudformation describe-stacks --stack-name $stack_name | jq .Stacks[0].StackStatus`
   if [ $status == '"CREATE_COMPLETE"' ]; then
     echo -e "\nStack $stack_name completed successfully!!"
     get_outputs
   elif [ $status == '"CREATE_IN_PROGRESS"' ]; then
     sleep 5
     describe_stack
   fi
}

aws cloudformation create-stack --stack-name $stack_name --template-body file:///Users/kicky/vpc_creation.json --parameters ParameterKey="VPCRangeCidrBlock",ParameterValue=$cidr ParameterKey="PublicSubnetCidrBlock1",ParameterValue=$pub1 ParameterKey="PublicSubnetCidrBlock2",ParameterValue=$pub2 ParameterKey="PublicSubnetCidrBlock3",ParameterValue=$pub3 ParameterKey="PublicSubnetCidrBlock4",ParameterValue=$pub4 ParameterKey="PrivateSubnetCidrBlock1",ParameterValue=$pri1 ParameterKey="PrivateSubnetCidrBlock2",ParameterValue=$pri2 ParameterKey="PrivateSubnetCidrBlock3",ParameterValue=$pri3 ParameterKey="PrivateSubnetCidrBlock4",ParameterValue=$pri4

echo "CloudFormation stack created. Lets wait for the components to get created.........."
echo
progressbar 100
describe_stack
