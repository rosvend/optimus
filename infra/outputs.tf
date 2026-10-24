output "ingest_url" {
  description = "Public URL for POSTing and GETting readings"
  value       = module.lambda.function_url
}

output "api_key" {
  description = "Shared key sent as the x-api-key header"
  value       = random_password.api_key.result
  sensitive   = true
}

output "table_name" {
  description = "DynamoDB table holding the readings"
  value       = module.dynamodb.table_name
}

output "dashboard_url" {
  description = "Public URL of the telemetry dashboard"
  value       = module.dashboard.url
}
