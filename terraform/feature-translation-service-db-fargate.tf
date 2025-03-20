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

#----- ECS Container Image--------
resource "aws_ecr_repository" "lambda_image_repo_db" {
  name = local.ftsdb_resource_name
  tags = var.default_tags
}

resource "null_resource" "ecr_login_db" {
  triggers = {
    image_uri = var.docker_db_tag
  }
  provisioner "local-exec" {
    interpreter = ["/bin/sh", "-e", "-c"]
    command     = <<EOF
      docker login ${data.aws_ecr_authorization_token.token.proxy_endpoint} -u AWS -p ${data.aws_ecr_authorization_token.token.password}
      EOF
  }
}

resource "null_resource" "upload_ecr_image_db" {
  depends_on = [null_resource.ecr_login_db]
  triggers = {
    image_uri = var.docker_db_tag
  }
  provisioner "local-exec" {
    interpreter = ["/bin/sh", "-e", "-c"]
    command     = <<EOF
      docker pull ${var.docker_db_tag}
      docker tag ${var.docker_db_tag} ${aws_ecr_repository.lambda_image_repo_db.repository_url}:${local.ecr_image_tag_db}
      docker push ${aws_ecr_repository.lambda_image_repo_db.repository_url}:${local.ecr_image_tag_db}
      EOF
  }
}

#----- Fargate Task Definition --------
resource "aws_ecs_task_definition" "fargate_task" {
  family                   = "${local.ftsdb_resource_name}-fargate-task"
  requires_compatibilities = ["FARGATE"]
  container_definitions    = <<EOF
[
    {
        "name": "fts-sword-fargate-task",
        "image": "${aws_ecr_repository.lambda_image_repo_db.repository_url}:${data.aws_ecr_image.lambda_image_db.image_tag}",
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
