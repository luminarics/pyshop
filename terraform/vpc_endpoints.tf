# VPC Endpoints for cost optimization
# Gateway endpoints are FREE and avoid NAT gateway data transfer costs

# S3 Gateway Endpoint (FREE - no data transfer charges)
resource "aws_vpc_endpoint" "s3" {
  count             = var.enable_vpc_endpoints ? 1 : 0
  vpc_id            = aws_vpc.main.id
  service_name      = "com.amazonaws.${var.aws_region}.s3"
  vpc_endpoint_type = "Gateway"
  route_table_ids   = aws_route_table.private[*].id

  tags = {
    Name = "${var.project_name}-${var.environment}-s3-endpoint"
  }
}

# DynamoDB Gateway Endpoint (FREE - no data transfer charges)
resource "aws_vpc_endpoint" "dynamodb" {
  count             = var.enable_vpc_endpoints ? 1 : 0
  vpc_id            = aws_vpc.main.id
  service_name      = "com.amazonaws.${var.aws_region}.dynamodb"
  vpc_endpoint_type = "Gateway"
  route_table_ids   = aws_route_table.private[*].id

  tags = {
    Name = "${var.project_name}-${var.environment}-dynamodb-endpoint"
  }
}

# Security group for Interface VPC endpoints
resource "aws_security_group" "vpc_endpoints" {
  count       = var.enable_vpc_endpoints ? 1 : 0
  name_prefix = "${var.project_name}-${var.environment}-vpce-"
  description = "Security group for VPC endpoints"
  vpc_id      = aws_vpc.main.id

  ingress {
    from_port   = 443
    to_port     = 443
    protocol    = "tcp"
    cidr_blocks = [var.vpc_cidr]
    description = "HTTPS from VPC"
  }

  egress {
    from_port   = 0
    to_port     = 0
    protocol    = "-1"
    cidr_blocks = ["0.0.0.0/0"]
    description = "Allow all outbound"
  }

  tags = {
    Name = "${var.project_name}-${var.environment}-vpce-sg"
  }

  lifecycle {
    create_before_destroy = true
  }
}

# ECR API Endpoint (avoids NAT for pulling Docker images - $0.01/GB vs NAT $0.045/GB)
resource "aws_vpc_endpoint" "ecr_api" {
  count               = var.enable_vpc_endpoints ? 1 : 0
  vpc_id              = aws_vpc.main.id
  service_name        = "com.amazonaws.${var.aws_region}.ecr.api"
  vpc_endpoint_type   = "Interface"
  private_dns_enabled = true
  subnet_ids          = aws_subnet.private[*].id
  security_group_ids  = [aws_security_group.vpc_endpoints[0].id]

  tags = {
    Name = "${var.project_name}-${var.environment}-ecr-api-endpoint"
  }
}

# ECR Docker Endpoint (required for pulling images)
resource "aws_vpc_endpoint" "ecr_dkr" {
  count               = var.enable_vpc_endpoints ? 1 : 0
  vpc_id              = aws_vpc.main.id
  service_name        = "com.amazonaws.${var.aws_region}.ecr.dkr"
  vpc_endpoint_type   = "Interface"
  private_dns_enabled = true
  subnet_ids          = aws_subnet.private[*].id
  security_group_ids  = [aws_security_group.vpc_endpoints[0].id]

  tags = {
    Name = "${var.project_name}-${var.environment}-ecr-dkr-endpoint"
  }
}

# CloudWatch Logs Endpoint (avoids NAT for logging)
resource "aws_vpc_endpoint" "logs" {
  count               = var.enable_vpc_endpoints ? 1 : 0
  vpc_id              = aws_vpc.main.id
  service_name        = "com.amazonaws.${var.aws_region}.logs"
  vpc_endpoint_type   = "Interface"
  private_dns_enabled = true
  subnet_ids          = aws_subnet.private[*].id
  security_group_ids  = [aws_security_group.vpc_endpoints[0].id]

  tags = {
    Name = "${var.project_name}-${var.environment}-logs-endpoint"
  }
}

# Secrets Manager Endpoint (avoids NAT for secrets access)
resource "aws_vpc_endpoint" "secretsmanager" {
  count               = var.enable_vpc_endpoints ? 1 : 0
  vpc_id              = aws_vpc.main.id
  service_name        = "com.amazonaws.${var.aws_region}.secretsmanager"
  vpc_endpoint_type   = "Interface"
  private_dns_enabled = true
  subnet_ids          = aws_subnet.private[*].id
  security_group_ids  = [aws_security_group.vpc_endpoints[0].id]

  tags = {
    Name = "${var.project_name}-${var.environment}-secretsmanager-endpoint"
  }
}

# Cost comparison notes:
# - Gateway endpoints (S3, DynamoDB): FREE
# - Interface endpoints: ~$7.30/month per endpoint + $0.01/GB data processed
# - NAT Gateway: ~$32.40/month + $0.045/GB data processed
#
# If using VPC endpoints + disabling NAT gateway:
# Monthly savings = ~$32.40 (NAT) - ~$36.50 (5 interface endpoints) = -$4.10 (slight cost increase)
# BUT data transfer savings: $0.035/GB (NAT $0.045/GB vs VPC endpoint $0.01/GB)
# Break-even: ~117 GB/month data transfer
#
# Best strategy:
# - Dev: Use VPC endpoints + disable NAT gateway if < 100GB/month traffic
# - Prod: Use VPC endpoints + single NAT gateway for other internet needs
