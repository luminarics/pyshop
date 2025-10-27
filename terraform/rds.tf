# DB Subnet Group (only created if not using Aurora Serverless)
resource "aws_db_subnet_group" "main" {
  count       = var.use_aurora_serverless ? 0 : 1
  name_prefix = "${var.project_name}-${var.environment}-"
  subnet_ids  = aws_subnet.private[*].id

  tags = {
    Name = "${var.project_name}-${var.environment}-db-subnet-group"
  }

  lifecycle {
    create_before_destroy = true
  }
}

# RDS Parameter Group (only created if not using Aurora Serverless)
resource "aws_db_parameter_group" "postgres" {
  count       = var.use_aurora_serverless ? 0 : 1
  name_prefix = "${var.project_name}-${var.environment}-"
  family      = "postgres15"

  parameter {
    name  = "log_connections"
    value = "1"
  }

  parameter {
    name  = "log_disconnections"
    value = "1"
  }

  parameter {
    name  = "log_statement"
    value = "all"
  }

  tags = {
    Name = "${var.project_name}-${var.environment}-postgres-params"
  }

  lifecycle {
    create_before_destroy = true
  }
}

# Random password for database
resource "random_password" "db_password" {
  count   = var.use_aurora_serverless ? 0 : 1
  length  = 32
  special = false # Avoid special chars for easier connection string handling
}

# Secrets Manager secret for database password
resource "aws_secretsmanager_secret" "db_password" {
  count                   = var.use_aurora_serverless ? 0 : 1
  name_prefix             = "${var.project_name}-${var.environment}-db-password-"
  recovery_window_in_days = 7

  tags = {
    Name = "${var.project_name}-${var.environment}-db-password"
  }
}

resource "aws_secretsmanager_secret_version" "db_password" {
  count     = var.use_aurora_serverless ? 0 : 1
  secret_id = aws_secretsmanager_secret.db_password[0].id
  secret_string = jsonencode({
    username          = var.db_username
    password          = random_password.db_password[0].result
    engine            = "postgres"
    host              = aws_db_instance.postgres[0].address
    port              = aws_db_instance.postgres[0].port
    dbname            = var.db_name
    connection_string = "postgresql+asyncpg://${var.db_username}:${random_password.db_password[0].result}@${aws_db_instance.postgres[0].address}:${aws_db_instance.postgres[0].port}/${var.db_name}"
  })
}

# RDS PostgreSQL Instance (only created if not using Aurora Serverless)
resource "aws_db_instance" "postgres" {
  count          = var.use_aurora_serverless ? 0 : 1
  identifier     = "${var.project_name}-${var.environment}-postgres"
  engine         = "postgres"
  engine_version = var.db_engine_version

  instance_class    = var.db_instance_class
  allocated_storage = var.db_allocated_storage
  storage_type      = "gp3"
  storage_encrypted = true

  db_name  = var.db_name
  username = var.db_username
  password = random_password.db_password[0].result

  db_subnet_group_name   = aws_db_subnet_group.main[0].name
  parameter_group_name   = aws_db_parameter_group.postgres[0].name
  vpc_security_group_ids = [aws_security_group.rds.id]

  multi_az               = var.db_multi_az
  publicly_accessible    = false
  backup_retention_period = 7
  backup_window          = "03:00-04:00"
  maintenance_window     = "sun:04:00-sun:05:00"

  enabled_cloudwatch_logs_exports = ["postgresql", "upgrade"]

  skip_final_snapshot       = var.environment != "production"
  final_snapshot_identifier = var.environment == "production" ? "${var.project_name}-${var.environment}-final-snapshot-${formatdate("YYYY-MM-DD-hhmm", timestamp())}" : null

  deletion_protection = var.environment == "production"

  tags = {
    Name = "${var.project_name}-${var.environment}-postgres"
  }
}

# CloudWatch alarms for RDS (only created if not using Aurora Serverless)
resource "aws_cloudwatch_metric_alarm" "database_cpu" {
  count               = var.use_aurora_serverless ? 0 : 1
  alarm_name          = "${var.project_name}-${var.environment}-rds-cpu-utilization"
  comparison_operator = "GreaterThanThreshold"
  evaluation_periods  = "2"
  metric_name         = "CPUUtilization"
  namespace           = "AWS/RDS"
  period              = "300"
  statistic           = "Average"
  threshold           = "80"
  alarm_description   = "This metric monitors RDS CPU utilization"

  dimensions = {
    DBInstanceIdentifier = aws_db_instance.postgres[0].id
  }
}

resource "aws_cloudwatch_metric_alarm" "database_storage" {
  count               = var.use_aurora_serverless ? 0 : 1
  alarm_name          = "${var.project_name}-${var.environment}-rds-storage-space"
  comparison_operator = "LessThanThreshold"
  evaluation_periods  = "1"
  metric_name         = "FreeStorageSpace"
  namespace           = "AWS/RDS"
  period              = "300"
  statistic           = "Average"
  threshold           = "10000000000" # 10 GB
  alarm_description   = "This metric monitors RDS free storage space"

  dimensions = {
    DBInstanceIdentifier = aws_db_instance.postgres[0].id
  }
}
