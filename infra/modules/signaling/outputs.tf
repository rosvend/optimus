output "url" {
  description = "wss:// URL for the robot and the dashboard"
  value       = aws_apigatewayv2_stage.live.invoke_url
}
