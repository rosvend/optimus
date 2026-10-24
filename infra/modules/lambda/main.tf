data "aws_iam_role" "lab" {
  name = var.role_name
}

data "archive_file" "source" {
  type        = "zip"
  source_dir  = var.source_dir
  output_path = "${path.root}/build/${var.function_name}.zip"
  excludes    = ["tests/**", "requirements-dev.txt", "**/__pycache__/**", ".pytest_cache/**"]
}

resource "aws_cloudwatch_log_group" "function" {
  name              = "/aws/lambda/${var.function_name}"
  retention_in_days = var.log_retention_days
}

resource "aws_lambda_function" "function" {
  function_name    = var.function_name
  role             = data.aws_iam_role.lab.arn
  runtime          = var.runtime
  handler          = var.handler
  filename         = data.archive_file.source.output_path
  source_code_hash = data.archive_file.source.output_base64sha256
  memory_size      = var.memory_mb
  timeout          = var.timeout_s

  environment {
    variables = var.environment
  }

  depends_on = [aws_cloudwatch_log_group.function]
}

# Public endpoint; the handler rejects requests without the shared x-api-key
resource "aws_lambda_function_url" "function" {
  count = var.public_url ? 1 : 0

  function_name      = aws_lambda_function.function.function_name
  authorization_type = "NONE"

  # Lets the browser dashboard call the API; auth is the x-api-key header, not cookies
  cors {
    allow_origins = var.cors_allow_origins
    allow_methods = ["GET", "POST"]
    allow_headers = ["content-type", "x-api-key"]
    max_age       = 3600
  }
}
