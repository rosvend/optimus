output "ingest_url" {
  description = "Public URL for POSTing and GETting readings"
  value       = aws_lambda_function_url.telemetry.function_url
}

output "api_key" {
  description = "Shared key sent as the x-api-key header"
  value       = random_password.api_key.result
  sensitive   = true
}

output "table_name" {
  description = "DynamoDB table holding the readings"
  value       = aws_dynamodb_table.readings.name
}
