output "table_name" {
  description = "Name of the readings table"
  value       = aws_dynamodb_table.readings.name
}
