variable "api_app_name" {
  type    = string
  default = "fts-api"
}

variable "app_version" {
  type = string
}

variable "db_app_name" {
  default = "fts-db"
  type    = string
}

variable "default_tags" {
  type    = map(string)
  default = {}
}

variable "docker_api_tag" {
  type    = string
  default = "poodaac-cloud/podaac-ftsapi:latest"
}

variable "docker_db_tag" {
  type    = string
  default = "poodaac-cloud/podaac-ftsdb-sword:latest"
}

variable "lambda_package" {
  type = string
}

variable "region" {
  type    = string
  default = "us-west-2"
}

variable "stage" {
  type = string
}

#----- Fargate Variables--------
variable "logs_retention_days" {
  type        = number
  description = "(Optional) Retention days for logs of the Fargate task log group "
  default     = 30
}

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
