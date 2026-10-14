provider "aws" {
  region  = var.aws_region
  profile = var.aws_profile

  default_tags {
    tags = { Project = var.project_name }
  }
}

locals {
  function_name = "${var.project_name}-telemetry"
  lambda_dir    = "${path.module}/../lambda"
}

data "aws_iam_role" "lab" {
  name = var.lab_role_name
}

resource "aws_dynamodb_table" "readings" {
  name         = var.table_name
  billing_mode = "PAY_PER_REQUEST"
  hash_key     = "sensor"
  range_key    = "ts"

  attribute {
    name = "sensor"
    type = "S"
  }

  attribute {
    name = "ts"
    type = "S"
  }
}

data "archive_file" "lambda" {
  type        = "zip"
  source_dir  = local.lambda_dir
  output_path = "${path.module}/build/lambda.zip"
  excludes    = ["tests/**", "requirements-dev.txt", "**/__pycache__/**", ".pytest_cache/**"]
}

resource "random_password" "api_key" {
  length  = var.api_key_length
  special = false
}

resource "aws_cloudwatch_log_group" "lambda" {
  name              = "/aws/lambda/${local.function_name}"
  retention_in_days = var.log_retention_days
}

resource "aws_lambda_function" "telemetry" {
  function_name    = local.function_name
  role             = data.aws_iam_role.lab.arn
  runtime          = var.lambda_runtime
  handler          = "handler.lambda_handler"
  filename         = data.archive_file.lambda.output_path
  source_code_hash = data.archive_file.lambda.output_base64sha256
  memory_size      = var.lambda_memory_mb
  timeout          = var.lambda_timeout_s

  environment {
    variables = {
      TABLE_NAME = aws_dynamodb_table.readings.name
      API_KEY    = random_password.api_key.result
    }
  }

  depends_on = [aws_cloudwatch_log_group.lambda]
}

# Public endpoint; the handler rejects requests without the shared x-api-key
resource "aws_lambda_function_url" "telemetry" {
  function_name      = aws_lambda_function.telemetry.function_name
  authorization_type = "NONE"
}
