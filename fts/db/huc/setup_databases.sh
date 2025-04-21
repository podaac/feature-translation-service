#!/usr/bin/env sh

set -ex

TF_VENUE=$1
AWS_PROFILE=$2
CURRENTDATE=$(date +%s)

mkdir -p deploy

cat resources/DBuserData.sh | sed -e "s/\${tf_venue}/${TF_VENUE}/" > "deploy/DBuserData-${CURRENTDATE}.sh"

FTS_SUBNET=$(aws --profile $AWS_PROFILE ec2 describe-subnets \
    --filters "Name=tag:Name,Values=Private application*" \
    --query "Subnets[*].{Id:SubnetId}[0]" \
    --output text)

FTS_SGID=$(aws --profile $AWS_PROFILE ec2 describe-security-groups \
    --filters Name=tag:application,Values=service-fts-${TF_VENUE} \
    --query "SecurityGroups[*].{Id:GroupId}[0]" \
    --output text)

NGAP_AMI=$(aws --profile $AWS_PROFILE ssm get-parameter \
    --region us-west-2 \
    --name "/ngap/amis/image_id_al2023_x86" \
    --query 'Parameter.Value' \
    --output text)

aws ec2 run-instances \
    --image-id ${NGAP_AMI} \
    --tag-specifications "ResourceType=instance,Tags=[{Key=\"Name\",Value=\"svc-feature-translation-service-db-${TF_VENUE}-init\"}]" \
    --count 1 \
    --instance-type t2.micro \
    --subnet-id "$FTS_SUBNET" \
    --security-group-ids "$FTS_SGID" \
    --iam-instance-profile Name="svc-feature-translation-service-db-${TF_VENUE}-instance-profile" \
    --instance-initiated-shutdown-behavior terminate \
    --profile $AWS_PROFILE \
    --user-data "file://deploy/DBuserData-${CURRENTDATE}.sh"