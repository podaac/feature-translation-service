variable "app_name" {default = "fts-api"}
variable "db_app_name" {default = "fts-db"}
variable "stage" {}
variable "credentials" {}
variable "profile" { }
variable "vpc_id" {}
variable "private_subnets" {}
variable "docker_tag" {}
variable "default_vpc_sg" {}
variable "lambda_package" {}

variable "region" {
  default = "us-west-2"
}

variable "default_tags" {
  type = map(string)
  default = {}
}

variable "docker_tag" {
  default = "poodaac-cloud/podaac-ftsdb:latest"
}

#----- Fargate Variables--------
variable "platform_version" {
  type        = string
  description = "(Optional) Fargate platform version"
  default     = "LATEST"
}

variable "task_cpu" {
  type        = number
  description = "(Optional) CPU value for the Fargate task"
  default     = 1024
}

variable "task_memory" {
  type        = number
  description = "(Optional) Memory value for the Fargate task"
  default     = 8192
}

variable "logs_retention_days" {
  type        = number
  description = "(Optional) Retention days for logs of the Fargate task log group "
  default     = 30
}