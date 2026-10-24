output "url" {
  description = "Public URL of the dashboard"
  value       = "http://${aws_s3_bucket_website_configuration.site.website_endpoint}"
}
