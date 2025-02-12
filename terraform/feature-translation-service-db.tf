## Database Security Group
resource "aws_security_group" "service-db-sg" {
  description = "controls access to the database"

  vpc_id = var.vpc_id
  name   = "${local.ec2_resources_name}-sg"
  tags = local.default_tags
}

resource "aws_security_group_rule" "allow_self_in" {
  type        = "ingress"
  security_group_id = aws_security_group.service-db-sg.id
  protocol    = "tcp"
  from_port   = 3306
  to_port     = 3306
  self = true
}

resource "aws_security_group_rule" "allow_all_out" {
  type        = "egress"
  security_group_id = aws_security_group.service-db-sg.id
  from_port = 0
  to_port   = 0
  protocol  = "-1"
  cidr_blocks = [
    "0.0.0.0/0",
  ]
}

output "fts-db-sg-id" {
  value = aws_security_group.service-db-sg.id
}

resource "aws_db_subnet_group" "default" {
  name       = "${local.ec2_resources_name}-subnet"
  subnet_ids = var.private_subnets

  tags = local.default_tags
}

output "fts-db-subnet" {
  value = element(tolist(aws_db_subnet_group.default.subnet_ids),0)
}

resource "random_password" "db_pass" {
  length = 16
  special = false
}

resource "random_password" "db_user_pass" {
  length = 16
  special = false
}

## RDS Database
resource "aws_db_instance" "fts-database" {
  identifier           = "${local.ec2_resources_name}-rds"
  allocated_storage    = 20
  storage_type         = "gp2"
  engine               = "mysql"
  engine_version       = "5.7"
  instance_class       = "db.t2.micro"
  db_name                 = "ftsdb"
  username             = "ftsadmin"
  password             = random_password.db_pass.result
  parameter_group_name = "default.mysql5.7"
  multi_az             = "true"
  vpc_security_group_ids = [aws_security_group.service-db-sg.id]
  db_subnet_group_name  = aws_db_subnet_group.default.id
  skip_final_snapshot = true
  tags = local.default_tags
}

resource "aws_ssm_parameter" "fts-db-admin" {
  name  = "${local.ec2_resources_name}-admin"
  type  = "String"
  value = aws_db_instance.fts-database.username
  tags = local.default_tags
}

resource "aws_ssm_parameter" "fts-db-admin-pass" {
  name  = "${local.ec2_resources_name}-admin-pass"
  type  = "SecureString"
  value = aws_db_instance.fts-database.password
  tags = local.default_tags
}

resource "aws_ssm_parameter" "fts-db-user" {
  name  = "${local.ec2_resources_name}-user"
  type  = "String"
  value = "ftsuser"
  tags = local.default_tags
}

resource "aws_ssm_parameter" "fts-db-user-pass" {
  name  = "${local.ec2_resources_name}-user-pass"
  type  = "SecureString"
  value = random_password.db_user_pass.result
  tags = local.default_tags
}

resource "aws_ssm_parameter" "fts-db-host" {
  name  = "${local.ec2_resources_name}-host"
  type  = "String"
  value = aws_db_instance.fts-database.address
  tags = local.default_tags
}

resource "aws_ssm_parameter" "fts-db-name" {
  name  = "${local.ec2_resources_name}-name"
  type  = "String"
  value = aws_db_instance.fts-database.db_name
  tags = local.default_tags
}

resource "aws_ssm_parameter" "fts-db-sg" {
  name  = "${local.ec2_resources_name}-sg"
  type  = "String"
  value = aws_security_group.service-db-sg.id
  tags = local.default_tags
}
