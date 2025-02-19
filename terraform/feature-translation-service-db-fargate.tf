#----- AWS ECS Cluster--------
resource "aws_ecs_cluster" "fargate-cluster" {
  name = "${local.ftsdb_resource_name}-fargate-cluster"
  tags = local.default_tags
}

#----- ECS  Services--------
resource "aws_cloudwatch_log_group" "fargate-task-log-group" {
  name              = "${local.ftsdb_resource_name}-fargate-worker"
  retention_in_days = 60
  tags              = local.default_tags
}

#----- Fargate Task Definition --------
resource "aws_ecs_task_definition" "fargate_task" {
  family                   = "${local.ftsdb_resource_name}-fargate-task"
  requires_compatibilities = ["FARGATE"]
  container_definitions    = <<EOF
[
    {
        "name": "fts-sword-fargate-task",
        "image": "${data.aws_caller_identity.current.account_id}.dkr.ecr.us-west-2.amazonaws.com/${var.docker_db_tag}",
        "secrets": [{
          "name": "DB_PASS",
          "valueFrom": "${aws_ssm_parameter.fts-db-user-pass.arn}"
        }],
        "environment": [{
          "name": "DB_HOST",
          "value": "${aws_ssm_parameter.fts-db-host.value}"
        },
        {
          "name": "DB_USER",
          "value": "${aws_ssm_parameter.fts-db-user.value}"
        },
        {
          "name": "DB_NAME",
          "value": "${aws_ssm_parameter.fts-db-name.value}"
        },
        {
          "name": "SWORD_S3_BUCKET",
          "value": "podaac-services-${local.environment}-deploy"
        },
        {
          "name": "SWORD_S3_PATH",
          "value": "internal/SWORD/Reaches_Nodes"
        }],
        "logConfiguration": {
            "logDriver": "awslogs",
            "options": {
                "awslogs-region": "us-west-2",
                "awslogs-group": "${aws_cloudwatch_log_group.fargate-task-log-group.name}",
                "awslogs-stream-prefix": "${aws_cloudwatch_log_group.fargate-task-log-group.name}"
            }
        }
    }
]
EOF

  network_mode = "awsvpc"
  cpu          = var.task_cpu
  memory       = var.task_memory

  execution_role_arn = aws_iam_role.fargate-task-execution-role.arn
  task_role_arn      = aws_iam_role.ecs_task_role.arn
  tags               = local.default_tags
}

#----- CloudWatch Log Group --------
resource "aws_cloudwatch_log_group" "logs" {
  name              = "/ecs/${local.ftsdb_resource_name}-fargate-task-logs"
  retention_in_days = var.logs_retention_days
  tags              = local.default_tags
}
