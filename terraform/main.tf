# configure the S3 backend for storing state. This allows different
# team members to control and update terraform state.
terraform {
  backend "s3" {
    region  = "us-west-2"
    encrypt = true
  }
}

provider "aws" {
  region = "us-west-2"

  ignore_tags {
    key_prefixes = ["gsfc-ngap"]
  }
}

locals {
  environment = lower(var.stage)

  account_id = data.aws_caller_identity.current.account_id

  # This is the convention we use to know what belongs to each other
  ftsapi_resource_name = "svc-${var.api_app_name}-${local.environment}"

  # Used to refer to the FTS database resources by the same convention
  ftsdb_resource_name = "svc-${var.db_app_name}-${local.environment}"

  lambda_container_image_uri_split_api = split("/", var.docker_api_tag)
  ecr_image_name_and_tag_api           = split(":", element(local.lambda_container_image_uri_split_api, length(local.lambda_container_image_uri_split_api) - 1))
  ecr_image_tag_api                    = element(local.ecr_image_name_and_tag_api, 1)

  lambda_container_image_uri_split_db = split("/", var.docker_api_tag)
  ecr_image_name_and_tag_db           = split(":", element(local.lambda_container_image_uri_split_db, length(local.lambda_container_image_uri_split_db) - 1))
  ecr_image_tag_db                    = element(local.ecr_image_name_and_tag_db, 1)

  default_tags = length(var.default_tags) == 0 ? {
    team : "TVA",
    application : "service-fts-${local.environment}",
    Environment = var.stage
    Version     = var.app_version
  } : var.default_tags
}

data "aws_caller_identity" "current" {}

data "aws_ecr_authorization_token" "token" {}

data "aws_ecr_image" "lambda_image_api" {
  depends_on = [
    null_resource.upload_ecr_image_api
  ]
  repository_name = aws_ecr_repository.lambda_image_repo_api.name
  image_tag       = local.ecr_image_tag_api
}

data "aws_ecr_image" "lambda_image_db" {
  depends_on = [
    null_resource.upload_ecr_image_db
  ]
  repository_name = aws_ecr_repository.lambda_image_repo_db.name
  image_tag       = local.ecr_image_tag_db
}

data "aws_subnet" "private_application_subnet" {
  for_each = toset(data.aws_subnets.private_application_subnets.ids)
  id       = each.value
}

data "aws_subnets" "private_application_subnets" {
  filter {
    name   = "vpc-id"
    values = [data.aws_vpc.vpc_id.id]
  }
  filter {
    name   = "tag:Name"
    values = ["Private application*"]
  }
}

data "aws_vpc" "vpc_id" {
  tags = {
    "Name" : "Application VPC"
  }
}