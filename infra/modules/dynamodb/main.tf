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
