#!/usr/bin/env bash

# https://aws.amazon.com/premiumsupport/knowledge-center/ec2-linux-log-user-data/
exec > >(tee /var/log/user-data.log|logger -t user-data -s 2>/dev/console) 2>&1

set -ex

# Update all packages
dnf update -y
# Install mysql client
dnf install -y mariadb105
#get HUC database dump from S3
aws s3 cp s3://podaac-services-${tf_venue}-deploy/internal/HUC_Data.csv HUC_Data.csv

# Get Admin username, User username, Host, and Database name from SSM.
FTS_ADMIN=$(aws ssm get-parameter \
    --region us-west-2 \
    --name "service-fts-db-${tf_venue}-admin" \
    --query 'Parameter.Value' \
    --output text)

FTS_USER=$(aws ssm get-parameter \
    --region us-west-2 \
    --name "service-fts-db-${tf_venue}-user" \
    --with-decryption \
    --query 'Parameter.Value' \
    --output text)

FTS_RDS_HOST=$(aws ssm get-parameter \
    --region us-west-2 \
    --name "service-fts-db-${tf_venue}-host" \
    --query 'Parameter.Value' \
    --output text)

FTS_RDS_DBNAME=$(aws ssm get-parameter \
    --region us-west-2 \
    --name "service-fts-db-${tf_venue}-name" \
    --query 'Parameter.Value' \
    --output text)

# Retreive the admin password from SSM and write it to a configuation file.
# This avoids the need to give the username and password on the command line which is insecure and shows
# the password in the logs of the user data script.
# Note, we also turn off command echoing while writing the file.

set +x
cat << EOF > "/etc/my.cnf"
[client]
user=${FTS_ADMIN}
password=$(aws ssm get-parameter \
    --region us-west-2 \
    --name "service-fts-db-${tf_venue}-admin-pass" \
    --with-decryption \
    --query 'Parameter.Value' \
    --output text)
host=${FTS_RDS_HOST}
database=${FTS_RDS_DBNAME}
EOF
set -x

#drop table
mysql -e 'DROP TABLE IF EXISTS `huc_table`'
#create table
mysql -e 'CREATE TABLE IF NOT EXISTS `huc_table` (`HUC` varchar(50) DEFAULT NULL, `Region` varchar(500) DEFAULT NULL, `Polygon Convex Hull` text, `Polygon Visvalingam` text, `Bounding Box` varchar(255) DEFAULT NULL, KEY `Region` (`Region`) USING HASH,KEY `HUC` (`HUC`) USING HASH)'

#create a user for the lambda functions
# Retrieve user password from SSM. Do not echo command itself because that would display the password in the logs
set +x
echo "mysql -e \"grant SELECT, INSERT, DROP, UPDATE, INDEX, CREATE on ${FTS_RDS_DBNAME}.* to '${FTS_USER}'@'%' identified by '****'\""
mysql -e "grant SELECT, INSERT, DROP, UPDATE, INDEX, CREATE on ${FTS_RDS_DBNAME}.* to '${FTS_USER}'@'%' identified by '$(aws ssm get-parameter \
    --region us-west-2 \
    --name "service-fts-db-${tf_venue}-user-pass" \
    --with-decryption \
    --query 'Parameter.Value' \
    --output text)'"
set -x

#add data to the table
mysql -e "LOAD DATA LOCAL INFILE 'HUC_Data.csv' INTO TABLE ${FTS_RDS_DBNAME}.huc_table FIELDS TERMINATED BY ',' ENCLOSED BY '\"' IGNORE 1 LINES"

#shutdown the instance
shutdown
