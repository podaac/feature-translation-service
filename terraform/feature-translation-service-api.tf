
# SSM Parameter values
data "aws_ssm_parameter" "fts-db-sg" {
  name = "${local.ftsdb_resource_name}-sg"
}

#Security Groups

## Application Lambda Security Group
resource "aws_security_group" "service-app-sg" {
  description = "controls access to the lambda Application"
  vpc_id      = var.vpc_id
  name        = "${local.ec2_resources_name}-sg"

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
  function_name = "${local.ec2_resources_name}-0_2_1"
  role          = aws_iam_role.fts-service-role.arn
  package_type  = "Image"
  image_uri     = "${local.account_id}.dkr.ecr.us-west-2.amazonaws.com/podaac/podaac-cloud/podaac-fts:0.2.1"
  timeout       = 5

  vpc_config {
    subnet_ids         = var.private_subnets
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
  function_name = "${local.ec2_resources_name}-function"
  role          = aws_iam_role.fts-service-role.arn
  package_type  = "Image"
  image_uri     = "${local.account_id}.dkr.ecr.us-west-2.amazonaws.com/${var.docker_api_tag}"
  timeout       = 5

  vpc_config {
    subnet_ids         = var.private_subnets
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
  name        = "${local.ec2_resources_name}-api-gateway"
  description = "API to access Feature Translation Service"
  body = templatefile(
    "${path.module}/api_specification_templates/fts_aws_api.yml",
    {
      ftsapi_v021_lambda_arn = aws_lambda_function.fts_api_lambda_0_2_1.invoke_arn
      ftsapi_lambda_arn      = aws_lambda_function.fts_api_lambdav1.invoke_arn
      vpc_id                 = var.vpc_id
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
  name  = "fts-api-url"
  type  = "String"
  value = aws_api_gateway_deployment.fts-api-gateway-deployment.invoke_url
}

#########################
# CodeBuild functionality
#########################

#CodeBuild IAM role

resource "aws_iam_role" "fts-codebuild-iam" {
  name = "fts-codebuild"

  permissions_boundary = "arn:aws:iam::${data.aws_caller_identity.current.account_id}:policy/NGAPShRoleBoundary"
  assume_role_policy   = <<EOF
{
  "Version": "2012-10-17",
  "Statement": [
    {
      "Effect": "Allow",
      "Principal": {
        "Service": "codebuild.amazonaws.com"
      },
      "Action": "sts:AssumeRole"
    }
  ]
}
EOF
}

resource "aws_iam_role_policy" "fts-codebuild-policy" {
  role = aws_iam_role.fts-codebuild-iam.name


  policy = <<POLICY
{
    "Version": "2012-10-17",
    "Statement": [
        {
            "Sid": "CloudWatchLogsPolicy",
            "Effect": "Allow",
            "Action": [
                "logs:CreateLogGroup",
                "logs:CreateLogStream",
                "logs:PutLogEvents",
                "logs:GetLogEvents",
                "ssm:GetParameters",
                "ssm:GetParameter"
            ],
            "Resource": [
                "*"
            ]
        },
        {
            "Sid": "CodeCommitPolicy",
            "Effect": "Allow",
            "Action": [
                "codecommit:GitPull"
            ],
            "Resource": [
                "*"
            ]
        },
        {
            "Sid": "S3GetObjectPolicy",
            "Effect": "Allow",
            "Action": [
                "s3:GetObject",
                "s3:GetObjectVersion",
                "s3:List*"
            ],
            "Resource": [
                "*"
            ]
        },
        {
            "Sid": "S3PutObjectPolicy",
            "Effect": "Allow",
            "Action": [
                "s3:PutObject"
            ],
            "Resource": [
                "*"
            ]
        },
        {
            "Effect": "Allow",
            "Action": [
                "ec2:CreateNetworkInterfacePermission",
                "ec2:CreateNetworkInterface",
                "ec2:DescribeDhcpOptions",
                "ec2:DescribeNetworkInterfaces",
                "ec2:DeleteNetworkInterface",
                "ec2:DescribeSubnets",
                "ec2:DescribeSecurityGroups",
                "ec2:DescribeVpcs"
            ],
            "Resource": "*"
        },
        {
            "Effect": "Allow",
            "Resource": [
                "arn:aws:codebuild:us-west-2:206226843404:project/*"
            ],
            "Action": [
                "codebuild:StartBuild",
                "codebuild:BatchGetBuilds",
                "codebuild:BatchGetProjects"
            ]
        }
    ]
}
POLICY
}


#CodeBuild Project

resource "aws_codebuild_project" "fts" {
  name          = "FTS"
  description   = "FTS Postman Testing"
  build_timeout = "60"
  service_role  = aws_iam_role.fts-codebuild-iam.arn

  artifacts {
    packaging           = "NONE"
    name                = "fts-reports"
    namespace_type      = "BUILD_ID"
    encryption_disabled = false
    location            = "podaac-services-${var.stage}-deploy"
    path                = "internal/fts/test-reports"
    type                = "S3"
  }

  environment {
    compute_type                = "BUILD_GENERAL1_SMALL"
    image_pull_credentials_type = "CODEBUILD"
    privileged_mode             = false
    image                       = "aws/codebuild/standard:3.0"
    type                        = "LINUX_CONTAINER"
  }

  logs_config {
    cloudwatch_logs {
      status      = "ENABLED"
      group_name  = "codeBuild"
      stream_name = "FTS"
    }

    s3_logs {
      status = "DISABLED"
    }
  }

  source {
    insecure_ssl = false
    type         = "S3"
    location     = "podaac-services-${var.stage}-deploy/internal/fts/"
  }

  vpc_config {
    vpc_id = var.vpc_id

    subnets = var.private_subnets

    security_group_ids = [
      aws_security_group.service-app-sg.id
    ]
  }
}
