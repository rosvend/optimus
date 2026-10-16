output "function_url" {
  description = "Public URL of the function"
  value       = aws_lambda_function_url.function.function_url
}

output "function_name" {
  description = "Name of the function"
  value       = aws_lambda_function.function.function_name
}
