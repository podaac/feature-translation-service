
# Deploying the FTS API

## Dependencies
There are a handful of dependencies needed to deploy the entire Feature Translation Service

* Terraform - deployment technology.  >= Terraform v0.12.7
* AWS CLI - Amazon Web Service command line interface. >= aws-cli/1.11.120
* python3 environment - tested with python 3.7, needed for packaging the lambda functions.

## Soft dependencies
These are dependencies for deploying the entire Feature Translation Service that exist outside of this build.

* access key for NGAP environment
* Terraform variables defined below

## Terraform Variables

| variable        | Defined In   | Example                                                 | Description |
| --------------- | ------------ | ------------------------------------------------------- | ----------- |
| stage           | tf_vars      | sit                                                     | staging environment to which we are deploying |
| app_name        | tf_vars      | FTS                                                     | Name of the application being deployed - same for all environments|
| docker_tag      | command line | podaac/podaac-cloud/podaac-fts:1.0.0-alpha.3            | Name of docker image and tag as returned from `docker/build-docker.sh`. |
| vpc_id          | tf_vars      | vpc-abcdfc64e8ce5cca8                                   | VPC Id for use. This is predefined by NGAP. |
| private_subnets | tf_vars      | ["subnet-abcde06f25bd4047b","subnet-fghoj3417fedb7f05"] | private subnets for use within VPC. This is defined by NGAP |


## Building the lambda images
The lambda code needs to be built into a deployable image and uploaded to ECR before running terraform. Normally CI/CD handles this task but if you are trying to run terraform locally it needs to be done manually.

Follow the instructions in the [docker README](../docker/README.md) to build the image


## Build and deploy the application
We use a pre-built docker container to do the deployment (Please do not use local terraform!)

From the project root directory:
```
export tf_venue=sit
docker run -v ~/.aws:/home/dockeruser/.aws:ro -v ${PWD}:/home/dockeruser -w /home/dockeruser/terraform cae-artifactory.jpl.nasa.gov:16003/podaac/service/deploy-terraform-1.0.3:latest bash bin/deploy.sh -v ${tf_venue} -t ${docker_tag}
```

## Destroying the Application
Similarly, use the pre-built docker container to do the destroy (Please do not use local terraform!)

From the project root directory:
```
docker run -v ~/.aws:/home/dockeruser/.aws:ro -v ${PWD}:/home/dockeruser cae-artifactory.jpl.nasa.gov:16003/podaac/service/deploy-terraform-1.0.3:latest bash bin/destroy.sh -v ${tf_venue} -t ${docker_tag}
```
This will take anywhere from 3-10 minutes.

# Building the FTS Deployment DATABASE

## Dependencies
There are a handful of dependencies needed to deploy the entire Feature Translation Service

* Terraform - deployment technology.  >= Terraform v0.12.7
* AWS CLI - Amazon Web Service command line interface. >= aws-cli/1.11.120
* python3 environment - tested with python 3.7, needed for packaging the lambda functions.

## Soft dependencies
These are dependencies for deploying the entire Feature Translation Service that exist outside of this build.

* access key for NGAP environment
* Terraform variables defined below

## Terraform Variables

| variable        | Defined In   | Example                                                 | Description |
| --------------- | ------------ | ------------------------------------------------------- | ----------- |
| stage           | tf_vars      | sit                                                     | staging environment to which we are deploying |
| app_name        | tf_vars      | FTS                                                     | Name of the application being deployed - same for all environments|
| vpc_id          | tf_vars      | vpc-abcdfc64e8ce5cca8                                   | VPC Id for use. This is predefined by NGAP. |
| private_subnets | tf_vars      | ["subnet-abcde06f25bd4047b","subnet-fghoj3417fedb7f05"] | private subnets for use within VPC. This is defined by NGAP |

## Exports of configuration to use

## Select Venue

Determine the deployment target venue by setting the `tf_venue` environment varibale. For example, if deploying to SIT use:
```shell script
export tf_venue=sit
```
For UAT use:
```shell script
export tf_venue=uat
```

**Important** Your AWS credentials profile name must match the format `ngap-service-${tf_venue}` for the following commands to work.


## Copy the HUC Database to the ${venue} deployment account
```
aws s3 cp HUC_Data.csv s3://podaac-services-${tf_venue}-deploy/internal/HUC_Data.csv --profile ngap-service-${tf_venue}
```s

## Build and deploy the database

```shell script
docker run --env tf_venue=$tf_venue  -it -v  ~/.aws/credentials:/home/dockeruser/.aws/credentials -v ${PWD}:/home/dockeruser podaac-ci.jpl.nasa.gov:5000/services/deploy-terraform:12.24 /bin/bash ./bin/deploy.sh

```

which will run the following commands in docker:

```shell script
#terraform init -reconfigure -backend-config="bucket=podaac-services-${tf_venue}-terraform" -backend-config="profile=ngap-service-${tf_venue}"
#terraform plan -var-file=tfvars/${tf_venue}.tfvars
#terraform apply -auto-approve -var-file=tfvars/${tf_venue}.tfvars
```

## Populate Databases

*Note, we only need to run this the first time we setup the databases.*

Once deployed, we'll need to populate the HUC and SWOT Feature database. This is done automatically for us  in the setup_databases.sh script. This creates an EC2 instance in the venue's VPC and calls the resource/DBuserData.sh script on startup to create database tables, create lambda users, and populate the database with data. Once it's finished, it terminates itself.

```
export FTS_SGID="$(terraform output fts-db-sg-id)"
export FTS_SUBNET="$(terraform output fts-db-subnet)"
sh setup_databases.sh
```

Note: The above script assumes existence of a few environment varaibles, i.e., tf_venue, tf_profile, FTS_SGID, FTS_SUBNET.
FTS_SGID and FTS_SUBNET should be set to values of fts-db-sg-id and fts-db-subnet in the run output of "terraform apply" command above.


## Destroying the Database
Only one command is needed to destroy the database.

```shell script
terraform destroy -var-file=tfvars/${tf_venue}.tfvars
```

This will take anywhere from 3-10 minutes, depending on the RDS database deletion.
