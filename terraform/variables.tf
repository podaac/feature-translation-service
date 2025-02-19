variable "api_app_name" { default = "fts-api" }
variable "db_app_name" { default = "fts-db" }
variable "stage" {}
variable "vpc_id" {}
variable "private_subnets" {
  type = list(string)
}
variable "lambda_package" {}

variable "region" {
  default = "us-west-2"
}

variable "default_tags" {
  type    = map(string)
  default = {}
}

variable "docker_api_tag" {
  default = "poodaac-cloud/podaac-ftsapi:latest"
}

variable "docker_db_tag" {
  default = "poodaac-cloud/podaac-ftsdb-sword:latest"
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