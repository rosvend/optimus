provider "aws" {
  region  = var.aws_region
  profile = var.aws_profile

  default_tags {
    tags = { Project = var.project_name }
  }
}

resource "random_password" "api_key" {
  length  = var.api_key_length
  special = false
}

module "dynamodb" {
  source     = "./modules/dynamodb"
  table_name = var.table_name
}

module "lambda" {
  source             = "./modules/lambda"
  function_name      = "${var.project_name}-telemetry"
  role_name          = var.lab_role_name
  source_dir         = "${path.module}/lambda"
  handler            = "handler.lambda_handler"
  runtime            = var.lambda_runtime
  memory_mb          = var.lambda_memory_mb
  timeout_s          = var.lambda_timeout_s
  log_retention_days = var.log_retention_days
  cors_allow_origins = var.cors_allow_origins

  environment = {
    TABLE_NAME = module.dynamodb.table_name
    API_KEY    = random_password.api_key.result
  }
}

module "signaling_lambda" {
  source             = "./modules/lambda"
  function_name      = "${var.project_name}-signaling"
  role_name          = var.lab_role_name
  source_dir         = "${path.module}/signaling"
  handler            = "handler.lambda_handler"
  runtime            = var.lambda_runtime
  memory_mb          = var.lambda_memory_mb
  timeout_s          = var.lambda_timeout_s
  log_retention_days = var.log_retention_days
  public_url         = false

  environment = {
    TABLE_NAME = var.signaling_table_name
    API_KEY    = random_password.api_key.result
  }
}

module "signaling" {
  source               = "./modules/signaling"
  api_name             = "${var.project_name}-signaling"
  stage_name           = var.signaling_stage
  table_name           = var.signaling_table_name
  lambda_function_name = module.signaling_lambda.function_name
  lambda_invoke_arn    = module.signaling_lambda.invoke_arn
  throttle_burst       = var.signaling_throttle_burst
  throttle_rate        = var.signaling_throttle_rate
}

module "dashboard" {
  source        = "./modules/dashboard"
  bucket_prefix = "${var.project_name}-dashboard-"
  source_dir    = "${path.module}/../dashboard/dist"
  api_url       = module.lambda.function_url
  signaling_url = module.signaling.url
  video_room_id = var.video_room_id
  aws_profile   = var.aws_profile
  aws_region    = var.aws_region
}

# Resources were first created at the root; these keep them (and the URL) when moving into modules
moved {
  from = aws_dynamodb_table.readings
  to   = module.dynamodb.aws_dynamodb_table.readings
}

moved {
  from = aws_lambda_function.telemetry
  to   = module.lambda.aws_lambda_function.function
}

moved {
  from = aws_lambda_function_url.telemetry
  to   = module.lambda.aws_lambda_function_url.function
}

moved {
  from = aws_cloudwatch_log_group.lambda
  to   = module.lambda.aws_cloudwatch_log_group.function
}

moved {
  from = module.lambda.aws_lambda_function_url.function
  to   = module.lambda.aws_lambda_function_url.function[0]
}
