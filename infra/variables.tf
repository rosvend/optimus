variable "aws_profile" {
  description = "AWS CLI profile to deploy with"
  type        = string
}

variable "aws_region" {
  description = "Region for every resource"
  type        = string
}

variable "project_name" {
  description = "Prefix for resource names and the Project tag"
  type        = string
}

variable "lab_role_name" {
  description = "Existing IAM role the Lambda runs as (Academy accounts can't create roles)"
  type        = string
}

variable "table_name" {
  description = "DynamoDB table holding the readings"
  type        = string
}

variable "lambda_runtime" {
  description = "Lambda Python runtime"
  type        = string
}

variable "lambda_memory_mb" {
  description = "Lambda memory in MB"
  type        = number
}

variable "lambda_timeout_s" {
  description = "Lambda timeout in seconds"
  type        = number
}

variable "log_retention_days" {
  description = "Days to keep the Lambda's CloudWatch logs"
  type        = number
}

variable "api_key_length" {
  description = "Length of the generated shared API key"
  type        = number
}

variable "cors_allow_origins" {
  description = "Browser origins allowed to call the API (the dashboard)"
  type        = list(string)
}
