#!/usr/bin/env bash

set -Eexo pipefail

# Read in args from command line

POSITIONAL=()
while [[ $# -gt 0 ]]
do
key="$1"

case $key in
    -t|--docker-tag)
    docker_tag="$2"
    shift # past argument
    shift # past value
    ;;
    -l|--lambda)
    lambda_package="$2"
    shift # past argument
    shift # past value
    ;;
    -v|--tf-venue)
    tf_venue="$2"
    case $tf_venue in
     sit|uat|ops) ;;
     *)
        echo "tf_venue must be sit, uat, or ops"
        exit 1;;
    esac
    shift # past argument
    shift # past value
    ;;
    *)    # unknown option
    POSITIONAL+=("$1") # save it in an array for later
    shift # past argument
    ;;
esac
done
set -- "${POSITIONAL[@]}" # restore positional parameters

# https://www.terraform.io/docs/commands/environment-variables.html#tf_in_automation
TF_IN_AUTOMATION=true

# Terraform initialization
terraform init -reconfigure -input=false -backend-config="bucket=podaac-services-${tf_venue}-terraform" -backend-config="profile=ngap-service-${tf_venue}"


# If not deploying a specific docker tag, allow terraform to use the default value (see variables.tf for default value).
# Otherwise, supply the docker_tag variable to terraform.
if [[ -z "${docker_tag}" ]]; then
  terraform plan -input=false -var-file=tfvars/"${tf_venue}".tfvars -var="lambda_package=${lambda_package}" -out="tfplan"
else
  terraform plan -input=false -var-file=tfvars/"${tf_venue}".tfvars -var="lambda_package=${lambda_package}" -var="docker_tag=${docker_tag}" -out="tfplan"
fi

# Apply the plan that was created
terraform apply -input=false -auto-approve tfplan