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
  name        = var.api_app_name
  environment = lower(var.stage)

  account_id = data.aws_caller_identity.current.account_id

  # This is the convention we use to know what belongs to each other
  ftsapi_resource_name = "service-${var.api_app_name}-${local.environment}"

  # Used to refer to the FTS database resources by the same convention
  ftsdb_resource_name = "service-${var.db_app_name}-${local.environment}"

  default_tags = length(var.default_tags) == 0 ? {
    team : "TVA",
    application : "service-fts-${local.environment}",
    Environment = var.stage
    Version     = var.app_version
  } : var.default_tags
}

data "aws_caller_identity" "current" {}

data "aws_vpc" "vpc_id" {
  tags = {
    "Name" : "Application VPC"
  }
}

data "aws_subnet" "private_application_subnet" {
  for_each = toset(data.aws_subnets.private_application_subnets.ids)
  id       = each.value
}

data "aws_subnets" "private_application_subnets" {
  filter {
    name   = "vpc-id"
    values = [data.aws_vpc.application_vpc.id]
  }
  filter {
    name   = "tag:Name"
    values = ["Private application*"]
  }
}