# General
variable "project_name" {
  description = "Project name used for resource naming"
  type        = string
  default     = "pyshop"
}

variable "environment" {
  description = "Environment name (dev, staging, production)"
  type        = string
  default     = "dev"

  validation {
    condition     = contains(["dev", "staging", "production"], var.environment)
    error_message = "Environment must be dev, staging, or production."
  }
}

variable "aws_region" {
  description = "AWS region for resources"
  type        = string
  default     = "us-east-1"
}

# Networking
variable "vpc_cidr" {
  description = "CIDR block for VPC"
  type        = string
  default     = "10.0.0.0/16"
}

variable "public_subnet_cidrs" {
  description = "CIDR blocks for public subnets"
  type        = list(string)
  default     = ["10.0.1.0/24", "10.0.2.0/24"]
}

variable "private_subnet_cidrs" {
  description = "CIDR blocks for private subnets"
  type        = list(string)
  default     = ["10.0.10.0/24", "10.0.11.0/24"]
}

variable "enable_nat_gateway" {
  description = "Enable NAT Gateway for private subnets"
  type        = bool
  default     = true
}

variable "single_nat_gateway" {
  description = "Use single NAT Gateway for all AZs (saves ~$33/month but not HA)"
  type        = bool
  default     = true # Cost optimization: single NAT by default
}

variable "enable_vpc_endpoints" {
  description = "Enable VPC endpoints for AWS services (reduces NAT data transfer costs)"
  type        = bool
  default     = false # Set to true to save on NAT data transfer
}

# Application
variable "app_image" {
  description = "Docker image for the application"
  type        = string
  default     = "pyshop-api:latest"
}

variable "app_port" {
  description = "Port the application runs on"
  type        = number
  default     = 8000
}

variable "app_count" {
  description = "Number of application instances to run"
  type        = number
  default     = 1 # Cost optimization: start with 1, auto-scaling will add more if needed
}

# ECS Fargate
variable "fargate_cpu" {
  description = "Fargate instance CPU units (1024 = 1 vCPU)"
  type        = string
  default     = "256" # Cost optimization: 0.25 vCPU (increase if needed)
}

variable "fargate_memory" {
  description = "Fargate instance memory in MB"
  type        = string
  default     = "512" # Cost optimization: 0.5 GB (increase if needed)
}

variable "enable_fargate_spot" {
  description = "Enable Fargate Spot for 70% cost savings (may be interrupted)"
  type        = bool
  default     = true # Cost optimization: use Spot by default
}

variable "fargate_spot_weight" {
  description = "Percentage of tasks to run on Spot (0-100)"
  type        = number
  default     = 100 # 100% Spot for maximum savings

  validation {
    condition     = var.fargate_spot_weight >= 0 && var.fargate_spot_weight <= 100
    error_message = "Spot weight must be between 0 and 100."
  }
}

variable "fargate_base_tasks" {
  description = "Number of tasks to always run on regular Fargate (not Spot)"
  type        = number
  default     = 0 # No base tasks by default for maximum cost savings
}

# Auto Scaling
variable "autoscaling_min_capacity" {
  description = "Minimum number of tasks"
  type        = number
  default     = 1 # Cost optimization: start with 1
}

variable "autoscaling_max_capacity" {
  description = "Maximum number of tasks"
  type        = number
  default     = 4 # Cost optimization: reduced from 10
}

# Database
variable "db_name" {
  description = "Database name"
  type        = string
  default     = "pyshop"
}

variable "db_username" {
  description = "Database master username"
  type        = string
  default     = "app"
}

variable "db_instance_class" {
  description = "RDS instance class"
  type        = string
  default     = "db.t4g.micro"
}

variable "db_allocated_storage" {
  description = "Allocated storage for RDS in GB"
  type        = number
  default     = 20
}

variable "db_engine_version" {
  description = "PostgreSQL engine version"
  type        = string
  default     = "15.5"
}

variable "db_multi_az" {
  description = "Enable Multi-AZ deployment"
  type        = bool
  default     = false
}

# Aurora Serverless v2 (alternative to RDS)
variable "use_aurora_serverless" {
  description = "Use Aurora Serverless v2 instead of RDS (better for variable workloads)"
  type        = bool
  default     = false
}

variable "aurora_engine_version" {
  description = "Aurora PostgreSQL engine version"
  type        = string
  default     = "15.4"
}

variable "aurora_min_capacity" {
  description = "Minimum Aurora Serverless v2 capacity in ACUs (0.5 = ~$0.06/hour)"
  type        = number
  default     = 0.5

  validation {
    condition     = var.aurora_min_capacity >= 0.5 && var.aurora_min_capacity <= 128
    error_message = "Aurora min capacity must be between 0.5 and 128 ACUs."
  }
}

variable "aurora_max_capacity" {
  description = "Maximum Aurora Serverless v2 capacity in ACUs"
  type        = number
  default     = 2.0

  validation {
    condition     = var.aurora_max_capacity >= 0.5 && var.aurora_max_capacity <= 128
    error_message = "Aurora max capacity must be between 0.5 and 128 ACUs."
  }
}

# Logging
variable "log_retention_days" {
  description = "CloudWatch log retention in days"
  type        = number
  default     = 7
}

# DNS & SSL
variable "enable_ssl" {
  description = "Enable SSL/TLS with ACM certificate"
  type        = bool
  default     = false
}

variable "domain_name" {
  description = "Domain name for the application"
  type        = string
  default     = ""
}

variable "create_route53_zone" {
  description = "Create a new Route53 hosted zone"
  type        = bool
  default     = false
}

variable "route53_zone_id" {
  description = "Existing Route53 zone ID (required if create_route53_zone is false and enable_ssl is true)"
  type        = string
  default     = ""
}

# Application Configuration
variable "jwt_expire_minutes" {
  description = "JWT token expiration time in minutes"
  type        = number
  default     = 30
}
