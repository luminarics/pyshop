# VPC
output "vpc_id" {
  description = "ID of the VPC"
  value       = aws_vpc.main.id
}

output "public_subnet_ids" {
  description = "IDs of public subnets"
  value       = aws_subnet.public[*].id
}

output "private_subnet_ids" {
  description = "IDs of private subnets"
  value       = aws_subnet.private[*].id
}

# Load Balancer
output "alb_dns_name" {
  description = "DNS name of the Application Load Balancer"
  value       = aws_lb.main.dns_name
}

output "alb_zone_id" {
  description = "Zone ID of the Application Load Balancer"
  value       = aws_lb.main.zone_id
}

output "alb_url" {
  description = "URL of the Application Load Balancer"
  value       = var.enable_ssl ? "https://${var.domain_name}" : "http://${aws_lb.main.dns_name}"
}

# ECS
output "ecs_cluster_name" {
  description = "Name of the ECS cluster"
  value       = aws_ecs_cluster.main.name
}

output "ecs_cluster_id" {
  description = "ID of the ECS cluster"
  value       = aws_ecs_cluster.main.id
}

output "ecs_service_name" {
  description = "Name of the ECS service"
  value       = aws_ecs_service.app.name
}

output "ecs_task_definition_arn" {
  description = "ARN of the ECS task definition"
  value       = aws_ecs_task_definition.app.arn
}

# Database
output "db_instance_endpoint" {
  description = "Connection endpoint for the database"
  value       = var.use_aurora_serverless ? (length(aws_rds_cluster.aurora) > 0 ? aws_rds_cluster.aurora[0].endpoint : null) : (length(aws_db_instance.postgres) > 0 ? aws_db_instance.postgres[0].endpoint : null)
  sensitive   = true
}

output "db_instance_name" {
  description = "Name of the database"
  value       = var.db_name
}

output "db_instance_identifier" {
  description = "Identifier of the database instance"
  value       = var.use_aurora_serverless ? (length(aws_rds_cluster.aurora) > 0 ? aws_rds_cluster.aurora[0].id : null) : (length(aws_db_instance.postgres) > 0 ? aws_db_instance.postgres[0].id : null)
}

output "db_secrets_arn" {
  description = "ARN of the Secrets Manager secret containing database credentials"
  value       = var.use_aurora_serverless ? (length(aws_secretsmanager_secret.aurora_password) > 0 ? aws_secretsmanager_secret.aurora_password[0].arn : null) : (length(aws_secretsmanager_secret.db_password) > 0 ? aws_secretsmanager_secret.db_password[0].arn : null)
  sensitive   = true
}

# Application Secrets
output "app_secrets_arn" {
  description = "ARN of the Secrets Manager secret containing application secrets"
  value       = aws_secretsmanager_secret.app_secrets.arn
  sensitive   = true
}

# Security Groups
output "alb_security_group_id" {
  description = "ID of the ALB security group"
  value       = aws_security_group.alb.id
}

output "ecs_tasks_security_group_id" {
  description = "ID of the ECS tasks security group"
  value       = aws_security_group.ecs_tasks.id
}

output "rds_security_group_id" {
  description = "ID of the RDS security group"
  value       = aws_security_group.rds.id
}

# DNS
output "route53_zone_id" {
  description = "ID of the Route53 hosted zone"
  value       = var.enable_ssl && var.create_route53_zone ? aws_route53_zone.main[0].zone_id : var.route53_zone_id
}

output "route53_name_servers" {
  description = "Name servers for the Route53 hosted zone"
  value       = var.enable_ssl && var.create_route53_zone ? aws_route53_zone.main[0].name_servers : []
}

output "acm_certificate_arn" {
  description = "ARN of the ACM certificate"
  value       = var.enable_ssl ? aws_acm_certificate.main[0].arn : ""
}

# Monitoring
output "cloudwatch_log_group_name" {
  description = "Name of the CloudWatch log group"
  value       = aws_cloudwatch_log_group.app.name
}

output "cloudwatch_dashboard_name" {
  description = "Name of the CloudWatch dashboard"
  value       = aws_cloudwatch_dashboard.main.dashboard_name
}

output "sns_alarms_topic_arn" {
  description = "ARN of the SNS topic for alarms"
  value       = aws_sns_topic.alarms.arn
}

# Connection String (for local development)
output "database_connection_string" {
  description = "PostgreSQL connection string (for reference, use Secrets Manager in production)"
  value       = var.use_aurora_serverless ? (length(aws_rds_cluster.aurora) > 0 ? "postgresql+asyncpg://${var.db_username}:<password>@${aws_rds_cluster.aurora[0].endpoint}/${var.db_name}" : null) : (length(aws_db_instance.postgres) > 0 ? "postgresql+asyncpg://${var.db_username}:<password>@${aws_db_instance.postgres[0].endpoint}/${var.db_name}" : null)
  sensitive   = true
}
