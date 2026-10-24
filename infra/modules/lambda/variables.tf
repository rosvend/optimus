variable "function_name" {
  description = "Lambda function name"
  type        = string
}

variable "role_name" {
  description = "Existing IAM role the function runs as (Academy accounts can't create roles)"
  type        = string
}

variable "source_dir" {
  description = "Directory with the Python source to zip"
  type        = string
}

variable "handler" {
  description = "Entry point as module.function"
  type        = string
}

variable "runtime" {
  description = "Lambda runtime"
  type        = string
}

variable "memory_mb" {
  description = "Memory in MB"
  type        = number
}

variable "timeout_s" {
  description = "Timeout in seconds"
  type        = number
}

variable "log_retention_days" {
  description = "Days to keep CloudWatch logs"
  type        = number
}

variable "environment" {
  description = "Environment variables for the function"
  type        = map(string)
  sensitive   = true
}

variable "cors_allow_origins" {
  description = "Browser origins allowed to call the function URL"
  type        = list(string)
  default     = []
}

variable "public_url" {
  description = "Expose the function on a public Function URL"
  type        = bool
  default     = true
}
