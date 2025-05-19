#IAM roles

resource "aws_iam_instance_profile" "fts-service-profile" {
  name = "${local.ftsapi_resource_name}-instance-profile"
  role = aws_iam_role.fts-service-role.name
}

resource "aws_iam_policy" "fts-service-policy" {
  name   = "${local.ftsapi_resource_name}-service-policy"
  path   = "/"
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
            "ec2:DeleteNetworkInterface"
          ],
          "Resource": "*"
      },
      {
          "Effect": "Allow",
          "Action": [
              "s3:GetAccelerateConfiguration",
              "s3:GetLifecycleConfiguration",
              "s3:GetReplicationConfiguration",
              "s3:GetBucket*",
              "s3:PutAccelerateConfiguration",
              "s3:PutLifecycleConfiguration",
              "s3:PutReplicationConfiguration",
              "s3:PutBucket*",
              "s3:ListBucket*"
          ],
          "Resource": [
                  "arn:aws:s3:::podaac-${var.stage}-service-work",
                  "arn:aws:s3:::podaac-${var.stage}-service-work/*"
          ]
      },
      {
          "Effect": "Allow",
          "Action": [
              "s3:AbortMultipartUpload",
              "s3:GetObject*",
              "s3:PutObject*",
              "s3:ListMultipartUploadParts",
              "s3:DeleteObject",
              "s3:DeleteObjectVersion"
          ],
          "Resource": [
              "arn:aws:s3:::podaac-${var.stage}-service-work",
              "arn:aws:s3:::podaac-${var.stage}-service-work/*"
          ]
      },
      {
          "Effect": "Allow",
          "Action": [
              "s3:ListAllMyBuckets"
          ],
          "Resource": "*"
      }
  ]
}
POLICY
}

resource "aws_iam_role" "fts-service-role" {
  name = "${local.ftsapi_resource_name}-service-role"

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

resource "aws_iam_policy_attachment" "fts-service-attach" {
  name       = "${local.ftsapi_resource_name}-attachment"
  roles      = [aws_iam_role.fts-service-role.id]
  policy_arn = aws_iam_policy.fts-service-policy.arn
}
