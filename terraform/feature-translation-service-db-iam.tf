#IAM roles
resource "aws_iam_instance_profile" "fts-service-db-profile" {
  name = "${local.ec2_resources_name}-instance-profile"
  role = aws_iam_role.fts-service-db-role.name
}

resource "aws_iam_policy" "fts-service-db-policy" {
  name = "${local.ec2_resources_name}-policy"
  path = "/"


  policy = <<POLICY
{
  "Version": "2012-10-17",
  "Statement": [
      {
          "Sid": "fromAWSSSMManagedInstanceCore1of3",
          "Effect": "Allow",
          "Action": [
              "ssm:DescribeAssociation",
              "ssm:GetDeployablePatchSnapshotForInstance",
              "ssm:GetDocument",
              "ssm:DescribeDocument",
              "ssm:GetManifest",
              "ssm:GetParameter",
              "ssm:GetParameters",
              "ssm:ListAssociations",
              "ssm:ListInstanceAssociations",
              "ssm:PutInventory",
              "ssm:PutComplianceItems",
              "ssm:PutConfigurePackageResult",
              "ssm:UpdateAssociationStatus",
              "ssm:UpdateInstanceAssociationStatus",
              "ssm:UpdateInstanceInformation"
          ],
          "Resource": "*"
      },
      {
          "Sid": "fromAWSSSMManagedInstanceCore2of3",
          "Effect": "Allow",
          "Action": [
              "ssmmessages:CreateControlChannel",
              "ssmmessages:CreateDataChannel",
              "ssmmessages:OpenControlChannel",
              "ssmmessages:OpenDataChannel"
          ],
          "Resource": "*"
      },
      {
          "Sid": "fromAWSSSMManagedInstanceCore3of3",
          "Effect": "Allow",
          "Action": [
              "ec2messages:AcknowledgeMessage",
              "ec2messages:DeleteMessage",
              "ec2messages:FailMessage",
              "ec2messages:GetEndpoint",
              "ec2messages:GetMessages",
              "ec2messages:SendReply"
          ],
          "Resource": "*"
      },
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
              "s3:Get*"
          ],
          "Resource": [
                  "arn:aws:s3:::podaac-services-${var.stage}-deploy",
                  "arn:aws:s3:::podaac-services-${var.stage}-deploy/*"
          ]
      }
  ]
}
POLICY
}

resource "aws_iam_role" "fts-service-db-role" {
  name = "${local.ec2_resources_name}-role"
  tags = local.default_tags

  permissions_boundary = "arn:aws:iam::${data.aws_caller_identity.current.account_id}:policy/NGAPShRoleBoundary"
  assume_role_policy   = <<EOF
{
  "Version": "2012-10-17",
  "Statement": [
    {
      "Action": "sts:AssumeRole",
      "Principal": {
        "Service": "ec2.amazonaws.com"
      },
      "Effect": "Allow",
      "Sid": ""
    }
  ]
}
EOF
}

resource "aws_iam_policy_attachment" "fts-service-db-attach" {
  name = "${local.ec2_resources_name}-attachment"
  roles = [
  aws_iam_role.fts-service-db-role.id]
  policy_arn = aws_iam_policy.fts-service-db-policy.arn
}
