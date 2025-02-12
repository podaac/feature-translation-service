#----- Lambda Policy Role --------
resource "aws_iam_role_policy" "lambda_policy" {
  name = "${local.ec2_resources_name}-lambda-policy"
  role = aws_iam_role.lambda-role.id

  policy = <<POLICY
{
  "Version": "2012-10-17",
  "Statement": [
      {
          "Effect": "Allow",
          "Action": [
            "cloudwatch:GetMetricStatistics",
            "logs:CreateLogGroup",
            "logs:CreateLogStream",
            "logs:DescribeLogStreams",
            "logs:PutLogEvents",
            "ssm:GetParameter",
            "ec2:CreateNetworkInterface",
            "ec2:DescribeNetworkInterfaces",
            "ec2:DeleteNetworkInterface",
            "ecs:RunTask",
            "ecs:ListTasks",
            "ecs:StartTask",
            "ecs:StopTask"
          ],
          "Resource": "*"
      },
      {
          "Effect": "Allow",
          "Action": [
              "iam:GetRole",
              "iam:PassRole"
          ],
          "Resource": [
              "${aws_iam_role.fargate-task-execution-role.arn}",
              "${aws_iam_role.ecs_task_role.arn}"
          ]
      },
      {
          "Effect": "Allow",
          "Action": [
                  "ecs:RunTask",
                  "ecs:ListTasks",
                  "ecs:StartTask",
                  "ecs:StopTask"
          ],
          "Condition": {
              "ArnEquals": {
                  "ecs:cluster": "${aws_ecs_cluster.fargate-cluster.arn}"
              }
          },
          "Resource": "*"
      }
  ]
}
POLICY
}

#----- Lambda IAM Role --------
resource "aws_iam_role" "lambda-role" {
  name                 = "${local.ec2_resources_name}-lambda-role"
  tags                 = local.default_tags
  permissions_boundary = "arn:aws:iam::${data.aws_caller_identity.current.account_id}:policy/NGAPShRoleBoundary"
  assume_role_policy   = <<EOF
{
  "Version": "2012-10-17",
  "Statement": [
    {
      "Action": "sts:AssumeRole",
      "Principal": {
        "Service": "lambda.amazonaws.com"
      },
      "Effect": "Allow",
      "Sid": ""
    }
  ]
}
EOF
}