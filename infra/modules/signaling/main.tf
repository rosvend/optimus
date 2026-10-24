# WebSocket API that relays WebRTC signaling between the robot and the dashboard
resource "aws_dynamodb_table" "connections" {
  name         = var.table_name
  billing_mode = "PAY_PER_REQUEST"
  hash_key     = "connectionId"

  attribute {
    name = "connectionId"
    type = "S"
  }

  attribute {
    name = "roomId"
    type = "S"
  }

  global_secondary_index {
    name            = "room"
    projection_type = "ALL"

    key_schema {
      attribute_name = "roomId"
      key_type       = "HASH"
    }
  }

  ttl {
    attribute_name = "expires"
    enabled        = true
  }
}

resource "aws_apigatewayv2_api" "signaling" {
  name                       = var.api_name
  protocol_type              = "WEBSOCKET"
  route_selection_expression = "$request.body.action"
}

resource "aws_apigatewayv2_integration" "lambda" {
  api_id           = aws_apigatewayv2_api.signaling.id
  integration_type = "AWS_PROXY"
  integration_uri  = var.lambda_invoke_arn
}

resource "aws_apigatewayv2_route" "route" {
  for_each = toset(["$connect", "$disconnect", "$default"])

  api_id    = aws_apigatewayv2_api.signaling.id
  route_key = each.value
  target    = "integrations/${aws_apigatewayv2_integration.lambda.id}"
}

resource "aws_apigatewayv2_stage" "live" {
  api_id      = aws_apigatewayv2_api.signaling.id
  name        = var.stage_name
  auto_deploy = true

  # Signaling is a handful of messages per call; this caps cost if the URL leaks
  default_route_settings {
    throttling_burst_limit = var.throttle_burst
    throttling_rate_limit  = var.throttle_rate
  }
}

resource "aws_lambda_permission" "api" {
  action        = "lambda:InvokeFunction"
  function_name = var.lambda_function_name
  principal     = "apigateway.amazonaws.com"
  source_arn    = "${aws_apigatewayv2_api.signaling.execution_arn}/*"
}
