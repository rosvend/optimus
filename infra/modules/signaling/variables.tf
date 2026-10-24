variable "api_name" {
  description = "Name of the WebSocket API"
  type        = string
}

variable "stage_name" {
  description = "Stage name, the last part of the WebSocket URL"
  type        = string
}

variable "table_name" {
  description = "DynamoDB table holding open connections"
  type        = string
}

variable "lambda_function_name" {
  description = "Function that handles every route"
  type        = string
}

variable "lambda_invoke_arn" {
  description = "Invoke ARN of that function"
  type        = string
}

variable "throttle_burst" {
  description = "Max burst of messages per second across the API"
  type        = number
}

variable "throttle_rate" {
  description = "Steady messages per second across the API"
  type        = number
}
