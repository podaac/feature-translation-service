#!/usr/bin/env sh

set -ex

CURRENTDATE=$(date +%s)
mkdir -p deploy
cat resources/DBuserData.sh | sed -e "s/\${tf_venue}/${tf_venue}/" > "deploy/DBuserData-${CURRENTDATE}.sh"

FTS_SUBNET=$(aws --profile ngap-service-${tf_venue} ec2 describe-subnets \
    --filters "Name=tag:Name,Values=Private application*" \
    --query "Subnets[*].{Id:SubnetId}[0]" \
    --output text)

FTS_SGID=$(aws --profile ngap-service-${tf_venue} ec2 describe-security-groups \
    --filters Name=tag:application,Values=service-fts-db-${tf_venue} \
    --query "SecurityGroups[*].{Id:GroupId}[0]" \
    --output text)

NGAP_AMI=$(aws --profile ngap-service-${tf_venue} ssm get-parameter \
    --region us-west-2 \
    --name "image_id_amz2" \
    --query 'Parameter.Value' \
    --output text)

aws ec2 run-instances \
    --image-id ${NGAP_AMI} \
    --tag-specifications "ResourceType=instance,Tags=[{Key=\"Name\",Value=\"service-fts-db-${tf_venue}-init\"}]" \
    --count 1 \
    --instance-type t2.micro \
    --subnet-id "$FTS_SUBNET" \
    --security-group-ids "$FTS_SGID" \
    --iam-instance-profile Name="service-fts-db-${tf_venue}-instance-profile" \
    --instance-initiated-shutdown-behavior terminate \
    --profile "ngap-service-${tf_venue}" \
    --user-data "file://deploy/DBuserData-${CURRENTDATE}.sh"