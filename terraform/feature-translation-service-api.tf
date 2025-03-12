
# SSM Parameter values
data "aws_ssm_parameter" "fts-db-sg" {
  name = "${local.ftsdb_resource_name}-sg"
}

#Security Groups

## Application Lambda Security Group
resource "aws_security_group" "service-app-sg" {
  description = "controls access to the lambda Application"
  vpc_id      = data.aws_vpc.vpc_id.id
  name        = "${local.ftsapi_resource_name}-sg"

  ingress {
    protocol    = "tcp"
    from_port   = 80
    to_port     = 80
    cidr_blocks = ["0.0.0.0/0"]
  }

  egress {
    from_port = 0
    to_port   = 0
    protocol  = "-1"

    cidr_blocks = [
      "0.0.0.0/0",
    ]
  }
}

## Allow ingress from the lambda security group to the database security group
resource "aws_security_group_rule" "allow_app_in" {
  type                     = "ingress"
  security_group_id        = data.aws_ssm_parameter.fts-db-sg.value
  protocol                 = "tcp"
  from_port                = 3306
  to_port                  = 3306
  source_security_group_id = aws_security_group.service-app-sg.id
}

# Lambda Function for the last stable pre-1.0 release of the API. This function is intended to be temprorary
# and should be removed once clients have moved off of this version (primarily, earthdata search client)
resource "aws_lambda_function" "fts_api_lambda_0_2_1" {
  function_name = "${local.ftsapi_resource_name}-0_2_1"
  role          = aws_iam_role.fts-service-role.arn
  package_type  = "Image"
  image_uri     = "${local.account_id}.dkr.ecr.us-west-2.amazonaws.com/podaac/podaac-cloud/podaac-fts:0.2.1"
  timeout       = 5

  vpc_config {
    subnet_ids         = data.aws_subnets.private_application_subnets.ids
    security_group_ids = [aws_security_group.service-app-sg.id]
  }

  environment {
    variables = {
      DB_HOST              = aws_ssm_parameter.fts-db-host.value
      DB_NAME              = aws_ssm_parameter.fts-db-name.value
      DB_USERNAME          = aws_ssm_parameter.fts-db-user.value
      DB_PASSWORD_SSM_NAME = aws_ssm_parameter.fts-db-user-pass.name
    }
  }

  tags = merge(local.default_tags, {
    "Version" : "0.2.1"
  })
}

resource "aws_lambda_permission" "allow_fts_0_2_1" {
  statement_id  = "AllowAPIGatewayInvoke"
  action        = "lambda:InvokeFunction"
  function_name = aws_lambda_function.fts_api_lambda_0_2_1.function_name
  principal     = "apigateway.amazonaws.com"

  # The "/*/*/*" portion grants access from any method on any resource
  # within the API Gateway REST API.
  source_arn = "${aws_api_gateway_rest_api.fts-api-gateway.execution_arn}/*/*/*"
}

resource "aws_api_gateway_deployment" "fts-api-gateway-deployment" {
  rest_api_id = aws_api_gateway_rest_api.fts-api-gateway.id
  depends_on  = [aws_api_gateway_rest_api.fts-api-gateway]
  triggers = {
    redeployment = sha1(jsonencode([
      aws_api_gateway_rest_api.fts-api-gateway.body
    ]))
  }
}

resource "aws_api_gateway_stage" "fts-api-gateway-stage" {
  deployment_id = aws_api_gateway_deployment.fts-api-gateway-deployment.id
  rest_api_id   = aws_api_gateway_rest_api.fts-api-gateway.id
  stage_name    = "default"
}

resource "aws_lambda_function" "fts_api_lambdav1" {
  function_name = "${local.ftsapi_resource_name}-function"
  role          = aws_iam_role.fts-service-role.arn
  package_type  = "Image"
  image_uri     = "${local.account_id}.dkr.ecr.us-west-2.amazonaws.com/${var.docker_api_tag}"
  timeout       = 5

  vpc_config {
    subnet_ids         = data.aws_subnets.private_application_subnets.ids
    security_group_ids = [aws_security_group.service-app-sg.id]
  }

  environment {
    variables = {
      DB_HOST              = aws_ssm_parameter.fts-db-host.value
      DB_NAME              = aws_ssm_parameter.fts-db-name.value
      DB_USERNAME          = aws_ssm_parameter.fts-db-user.value
      DB_PASSWORD_SSM_NAME = aws_ssm_parameter.fts-db-user-pass.name
    }
  }

  tags = var.default_tags
}

resource "aws_lambda_permission" "allow_fts" {
  statement_id  = "AllowAPIGatewayInvoke"
  action        = "lambda:InvokeFunction"
  function_name = aws_lambda_function.fts_api_lambdav1.function_name
  principal     = "apigateway.amazonaws.com"

  # The "/*/*/*" portion grants access from any method on any resource
  # within the API Gateway REST API.
  source_arn = "${aws_api_gateway_rest_api.fts-api-gateway.execution_arn}/*/*/*"
}

# API Gateway
resource "aws_api_gateway_rest_api" "fts-api-gateway" {
  name        = "${local.ftsapi_resource_name}-api-gateway"
  description = "API to access Feature Translation Service"
  body = templatefile(
    "${path.module}/api_specification_templates/fts_aws_api.yml",
    {
      ftsapi_v021_lambda_arn = aws_lambda_function.fts_api_lambda_0_2_1.invoke_arn
      ftsapi_lambda_arn      = aws_lambda_function.fts_api_lambdav1.invoke_arn
      vpc_id                 = data.aws_vpc.vpc_id.id
  })
  parameters = {
    "basemap" = "split"
  }
  endpoint_configuration {
    types = ["PRIVATE"]
  }
  lifecycle {
    prevent_destroy = true
  }
}

resource "aws_cloudwatch_log_group" "fts-api-gateway-logs" {
  name              = "API-Gateway-Execution-Logs_${aws_api_gateway_rest_api.fts-api-gateway.id}/${aws_api_gateway_stage.fts-api-gateway-stage.stage_name}"
  retention_in_days = 60
}

output "url" {
  value = "${aws_api_gateway_deployment.fts-api-gateway-deployment.invoke_url}/api"
}

resource "aws_ssm_parameter" "fts-api-url" {
  name  = "${local.ftsapi_resource_name}-api-url"
  type  = "String"
  value = aws_api_gateway_deployment.fts-api-gateway-deployment.invoke_url
}
