locals {
  content_types = {
    html = "text/html"
    css  = "text/css"
    js   = "text/javascript"
    json = "application/json"
    png  = "image/png"
    svg  = "image/svg+xml"
    ico  = "image/x-icon"
  }
  # config.json is generated below, so a local copy is never uploaded
  files = setsubtract(fileset(var.source_dir, "**"), ["config.json", "config.example.json"])

  bucket = {
    name    = "${var.bucket_prefix}${random_id.suffix.hex}"
    profile = var.aws_profile
    region  = var.aws_region
  }
}

resource "random_id" "suffix" {
  byte_length = 8
}

# The Academy SCP denies s3:GetBucketObjectLockConfiguration, which the aws_s3_bucket
# resource reads on every refresh, so the bucket itself is created with the CLI
resource "terraform_data" "bucket" {
  input = local.bucket

  provisioner "local-exec" {
    command = "aws s3api create-bucket --bucket ${self.input.name} --region ${self.input.region} --profile ${self.input.profile}"
  }

  provisioner "local-exec" {
    when    = destroy
    command = "aws s3 rb s3://${self.input.name} --force --region ${self.input.region} --profile ${self.input.profile}"
  }
}

resource "aws_s3_bucket_website_configuration" "site" {
  bucket = terraform_data.bucket.output.name

  index_document {
    suffix = "index.html"
  }
}

resource "aws_s3_bucket_public_access_block" "site" {
  bucket                  = terraform_data.bucket.output.name
  block_public_acls       = true
  ignore_public_acls      = true
  block_public_policy     = false
  restrict_public_buckets = false
}

resource "aws_s3_bucket_policy" "public_read" {
  bucket = terraform_data.bucket.output.name
  policy = jsonencode({
    Version = "2012-10-17"
    Statement = [{
      Effect    = "Allow"
      Principal = "*"
      Action    = "s3:GetObject"
      Resource  = "arn:aws:s3:::${terraform_data.bucket.output.name}/*"
    }]
  })

  depends_on = [aws_s3_bucket_public_access_block.site]
}

resource "aws_s3_object" "file" {
  for_each = local.files

  bucket       = terraform_data.bucket.output.name
  key          = each.value
  source       = "${var.source_dir}/${each.value}"
  etag         = filemd5("${var.source_dir}/${each.value}")
  content_type = lookup(local.content_types, reverse(split(".", each.value))[0], "application/octet-stream")
}

resource "aws_s3_object" "config" {
  bucket        = terraform_data.bucket.output.name
  key           = "config.json"
  content       = jsonencode({ apiUrl = var.api_url })
  content_type  = "application/json"
  cache_control = "no-cache"
}
