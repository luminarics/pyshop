# Aurora Serverless v2 - Alternative to RDS (pay-per-use, scales to zero)
# Cost: ~$0.12/hour when active (~$87/month if always on), but can pause when idle
# vs RDS db.t4g.micro: ~$15/month but always running

# Aurora Subnet Group
resource "aws_db_subnet_group" "aurora" {
  count      = var.use_aurora_serverless ? 1 : 0
  name_prefix = "${var.project_name}-${var.environment}-aurora-"
  subnet_ids  = aws_subnet.private[*].id

  tags = {
    Name = "${var.project_name}-${var.environment}-aurora-subnet-group"
  }

  lifecycle {
    create_before_destroy = true
  }
}

# Aurora Cluster Parameter Group
resource "aws_rds_cluster_parameter_group" "aurora" {
  count       = var.use_aurora_serverless ? 1 : 0
  name_prefix = "${var.project_name}-${var.environment}-aurora-"
  family      = "aurora-postgresql15"

  parameter {
    name  = "log_connections"
    value = "1"
  }

  parameter {
    name  = "log_disconnections"
    value = "1"
  }

  tags = {
    Name = "${var.project_name}-${var.environment}-aurora-params"
  }

  lifecycle {
    create_before_destroy = true
  }
}

# Random password for Aurora
resource "random_password" "aurora_password" {
  count   = var.use_aurora_serverless ? 1 : 0
  length  = 32
  special = false
}

# Aurora Serverless v2 Cluster
resource "aws_rds_cluster" "aurora" {
  count                     = var.use_aurora_serverless ? 1 : 0
  cluster_identifier        = "${var.project_name}-${var.environment}-aurora"
  engine                    = "aurora-postgresql"
  engine_mode               = "provisioned" # Required for Serverless v2
  engine_version            = var.aurora_engine_version
  database_name             = var.db_name
  master_username           = var.db_username
  master_password           = random_password.aurora_password[0].result
  db_subnet_group_name      = aws_db_subnet_group.aurora[0].name
  db_cluster_parameter_group_name = aws_rds_cluster_parameter_group.aurora[0].name
  vpc_security_group_ids    = [aws_security_group.rds.id]

  # Serverless v2 scaling configuration
  serverlessv2_scaling_configuration {
    min_capacity = var.aurora_min_capacity # 0.5 ACU minimum (~$0.06/hour)
    max_capacity = var.aurora_max_capacity # Maximum ACUs
  }

  # Backups
  backup_retention_period = 7
  preferred_backup_window = "03:00-04:00"
  preferred_maintenance_window = "sun:04:00-sun:05:00"

  # Storage
  storage_encrypted = true

  # Enable deletion protection for production
  deletion_protection = var.environment == "production"
  skip_final_snapshot = var.environment != "production"
  final_snapshot_identifier = var.environment == "production" ? "${var.project_name}-${var.environment}-aurora-final-${formatdate("YYYY-MM-DD-hhmm", timestamp())}" : null

  enabled_cloudwatch_logs_exports = ["postgresql"]

  tags = {
    Name = "${var.project_name}-${var.environment}-aurora-cluster"
  }
}

# Aurora Serverless v2 Instance
resource "aws_rds_cluster_instance" "aurora" {
  count              = var.use_aurora_serverless ? 1 : 0
  identifier         = "${var.project_name}-${var.environment}-aurora-instance"
  cluster_identifier = aws_rds_cluster.aurora[0].id
  instance_class     = "db.serverless" # Special instance class for Serverless v2
  engine             = aws_rds_cluster.aurora[0].engine
  engine_version     = aws_rds_cluster.aurora[0].engine_version

  performance_insights_enabled = var.environment == "production"

  tags = {
    Name = "${var.project_name}-${var.environment}-aurora-instance"
  }
}

# Secrets Manager for Aurora credentials
resource "aws_secretsmanager_secret" "aurora_password" {
  count                   = var.use_aurora_serverless ? 1 : 0
  name_prefix             = "${var.project_name}-${var.environment}-aurora-password-"
  recovery_window_in_days = 7

  tags = {
    Name = "${var.project_name}-${var.environment}-aurora-password"
  }
}

resource "aws_secretsmanager_secret_version" "aurora_password" {
  count     = var.use_aurora_serverless ? 1 : 0
  secret_id = aws_secretsmanager_secret.aurora_password[0].id
  secret_string = jsonencode({
    username          = var.db_username
    password          = random_password.aurora_password[0].result
    engine            = "postgres"
    host              = aws_rds_cluster.aurora[0].endpoint
    port              = aws_rds_cluster.aurora[0].port
    dbname            = var.db_name
    connection_string = "postgresql+asyncpg://${var.db_username}:${random_password.aurora_password[0].result}@${aws_rds_cluster.aurora[0].endpoint}:${aws_rds_cluster.aurora[0].port}/${var.db_name}"
  })
}

# CloudWatch alarms for Aurora
resource "aws_cloudwatch_metric_alarm" "aurora_cpu" {
  count               = var.use_aurora_serverless ? 1 : 0
  alarm_name          = "${var.project_name}-${var.environment}-aurora-cpu-utilization"
  comparison_operator = "GreaterThanThreshold"
  evaluation_periods  = "2"
  metric_name         = "CPUUtilization"
  namespace           = "AWS/RDS"
  period              = "300"
  statistic           = "Average"
  threshold           = "80"
  alarm_description   = "This metric monitors Aurora CPU utilization"

  dimensions = {
    DBClusterIdentifier = aws_rds_cluster.aurora[0].id
  }
}

resource "aws_cloudwatch_metric_alarm" "aurora_acu" {
  count               = var.use_aurora_serverless ? 1 : 0
  alarm_name          = "${var.project_name}-${var.environment}-aurora-acu-utilization"
  comparison_operator = "GreaterThanThreshold"
  evaluation_periods  = "2"
  metric_name         = "ServerlessDatabaseCapacity"
  namespace           = "AWS/RDS"
  period              = "300"
  statistic           = "Average"
  threshold           = var.aurora_max_capacity * 0.8
  alarm_description   = "Aurora Serverless approaching max capacity"

  dimensions = {
    DBClusterIdentifier = aws_rds_cluster.aurora[0].id
  }
}

# Cost optimization notes:
# Aurora Serverless v2 pricing:
# - 0.5 ACU minimum: $0.12/hour × 0.5 = $0.06/hour = $43.20/month (always on)
# - Scales automatically based on load
# - Can handle bursts efficiently
# - Better than RDS for variable workloads
# - More expensive than RDS t4g.micro ($15/month) for constant low traffic
#
# When to use Aurora Serverless v2:
# - Variable/unpredictable traffic patterns
# - Dev/staging with auto-pause capability
# - Need for quick scaling during bursts
#
# When to use RDS:
# - Constant, predictable traffic
# - Very low traffic (t4g.micro is cheapest)
# - Budget-constrained projects
