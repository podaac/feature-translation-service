#----- Lambda Function --------
resource "aws_lambda_function" "fts_sword_lambda" {
  filename         = var.lambda_package
  function_name    = "${local.ec2_resources_name}-lambda-fargate-function"
  role             = aws_iam_role.lambda-role.arn
  handler          = "sword_fargate.run_fargate_task"
  source_code_hash = filebase64sha256(var.lambda_package)
  runtime          = "python3.12"
  timeout          = 300

  # share fargate variables with lambda
  environment {
    variables = {
      REGION                 = var.region
      TASK_NAME              = aws_ecs_task_definition.fargate_task.arn
      FARGATE_CLUSTER        = aws_ecs_cluster.fargate-cluster.name
      FARGATE_SUBNET_ID      = element(tolist(aws_db_subnet_group.default.subnet_ids), 0)
      FARGATE_SECURITY_GROUP = aws_security_group.service-db-sg.id
    }
  }

  tags = local.default_tags
}