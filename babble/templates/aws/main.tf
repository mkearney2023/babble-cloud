terraform {
    required_providers {
        aws = {
            source = "hashicorp/aws"
            version = "= 4.52.0"
        }
        archive = {
            source = "hashicorp/archive"
            version = "= 2.3.0"
        }
        local = {
            source = "hashicorp/local"
            version = "= 2.3.0"
        }
    }
}
locals {
  state    = yamldecode(file("${path.module}/../state.yaml"))
  layer    = "${local.state.id}_layer"
  function = "${local.state.id}_function"
  api      = "${local.state.id}_api"
  packages = [for k, v in local.state.packages : k if v["source"] == "pip"]
}

resource "aws_dynamodb_table" "table" {
  for_each = local.state.tables
  name     = each.value.id
  attribute {
    name = each.value.key
    type = "S"
  }
  hash_key     = each.value.key
  billing_mode = "PAY_PER_REQUEST"
}
resource "aws_s3_bucket" "folder" {
    for_each = local.state.folders
    bucket   = each.value.id
    force_destroy = true
}

data "archive_file" "layer" {
  type        = "zip"
  output_path = "${path.module}/layer.zip"
  source {
    content  = file("${path.module}/layer.py")
    filename = "main.py"
  }
}
resource "aws_iam_role" "layer" {
  name = local.layer
  assume_role_policy = jsonencode({
    Version = "2012-10-17",
    Statement = [
      {
        Effect = "Allow",
        Principal = {
          Service = "lambda.amazonaws.com"
        },
        Action = "sts:AssumeRole"
      }
    ]
  })
}
resource "aws_iam_policy" "layer" {
  name = local.layer
  policy = jsonencode({
    Version = "2012-10-17",
    Statement = [
      {
        Effect   = "Allow",
        Action   = "*",
        Resource = "*"
      }
    ]
  })
}
resource "aws_iam_role_policy_attachment" "layer" {
  role       = aws_iam_role.layer.name
  policy_arn = aws_iam_policy.layer.arn
}
resource "aws_lambda_function" "layer" {
  function_name    = local.layer
  role             = aws_iam_role.layer.arn
  handler          = "main.handler"
  runtime          = "python3.9"
  memory_size      = 128
  timeout          = 900
  source_code_hash = data.archive_file.layer.output_base64sha256
  filename         = "layer.zip"
}
resource "aws_s3_bucket" "layer" {
  force_destroy = true
}
resource "aws_lambda_invocation" "layer" {
  function_name = aws_lambda_function.layer.function_name
  input = jsonencode({
    packages = local.packages
    bucket = aws_s3_bucket.layer.id
    key = "layer.zip"
  })
}
resource "aws_lambda_layer_version" "layer" {
  layer_name          = local.layer
  s3_bucket           = aws_s3_bucket.layer.id
  s3_key              = "layer.zip"
  compatible_runtimes = ["python3.9"]
  depends_on          = [aws_lambda_invocation.layer]
}

data "archive_file" "function" {
  type        = "zip"
  output_path = "${path.module}/function.zip"
  source {
    content  = file("${path.module}/function.py")
    filename = "main.py"
  }
  source {
    content  = jsonencode(local.state)
    filename = "state.json"
  }
}
resource "aws_iam_role" "function" {
  name = local.function
  assume_role_policy = jsonencode({
    Version = "2012-10-17",
    Statement = [
      {
        Effect = "Allow",
        Principal = {
          Service = "lambda.amazonaws.com"
        },
        Action = "sts:AssumeRole"
      }
    ]
  })
}
resource "aws_iam_policy" "function" {
  name = local.function
  policy = jsonencode({
    Version = "2012-10-17",
    Statement = [
      {
        Effect   = "Allow",
        Action   = "*",
        Resource = "*"
      }
    ]
  })
}
resource "aws_iam_role_policy_attachment" "function" {
  role       = aws_iam_role.function.name
  policy_arn = aws_iam_policy.function.arn
}
resource "aws_lambda_function" "function" {
  function_name    = local.function
  role             = aws_iam_role.function.arn
  handler          = "main.handler"
  runtime          = "python3.9"
  memory_size      = 128
  timeout          = 900
  source_code_hash = data.archive_file.function.output_base64sha256
  filename         = "function.zip"
  layers           = [aws_lambda_layer_version.layer.arn]
}

resource "aws_api_gateway_rest_api" "api" {
  name = local.api
}
resource "aws_api_gateway_resource" "api" {
  rest_api_id = aws_api_gateway_rest_api.api.id
  parent_id   = aws_api_gateway_rest_api.api.root_resource_id
  path_part   = "{proxy+}"
}
resource "aws_api_gateway_method" "api" {
  rest_api_id   = aws_api_gateway_rest_api.api.id
  resource_id   = aws_api_gateway_resource.api.id
  http_method   = "ANY"
  authorization = "NONE"
}
resource "aws_api_gateway_integration" "api" {
  rest_api_id             = aws_api_gateway_rest_api.api.id
  resource_id             = aws_api_gateway_resource.api.id
  http_method             = aws_api_gateway_method.api.http_method
  integration_http_method = "POST"
  type                    = "AWS_PROXY"
  uri                     = aws_lambda_function.function.invoke_arn
}
resource "aws_api_gateway_deployment" "api" {
  rest_api_id = aws_api_gateway_rest_api.api.id
  stage_name  = "api"
  depends_on  = [aws_api_gateway_integration.api]
}
resource "aws_lambda_permission" "api" {
  action        = "lambda:InvokeFunction"
  function_name = aws_lambda_function.function.function_name
  principal     = "apigateway.amazonaws.com"
  source_arn    = "${aws_api_gateway_rest_api.api.execution_arn}/*/*"
}
resource "local_file" "url" {
  content    = aws_api_gateway_deployment.api.invoke_url
  filename   = "url"
  depends_on = [aws_api_gateway_deployment.api]
}
