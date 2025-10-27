# Infrastructure Components

## Resource Overview

This Terraform configuration creates a complete AWS infrastructure for the PyShop API.

### Networking (network.tf)
- **VPC**: 10.0.0.0/16 CIDR block
- **Public Subnets**: 2 subnets across different AZs (10.0.1.0/24, 10.0.2.0/24)
- **Private Subnets**: 2 subnets for ECS tasks and RDS (10.0.10.0/24, 10.0.11.0/24)
- **Internet Gateway**: For public internet access
- **NAT Gateways**: 2 NAT gateways (one per AZ) for private subnet internet access
- **Route Tables**: Separate route tables for public and private subnets

### Security (security_groups.tf)
- **ALB Security Group**: Allows HTTP (80) and HTTPS (443) from internet
- **ECS Tasks Security Group**: Allows traffic from ALB on app port (8000)
- **RDS Security Group**: Allows PostgreSQL (5432) from ECS tasks only

### Database (rds.tf)
- **RDS PostgreSQL 15.5**: Managed database instance
- **Instance Class**: db.t4g.micro (configurable)
- **Storage**: 20GB GP3 encrypted storage
- **Backups**: 7-day retention, automated daily backups
- **High Availability**: Optional Multi-AZ deployment
- **Secrets Manager**: Secure credential storage with connection string
- **CloudWatch Alarms**: CPU and storage monitoring

### IAM (iam.tf)
- **ECS Task Execution Role**: For pulling images and accessing secrets
- **ECS Task Role**: For application runtime permissions
- **Secrets Access**: Permissions for Secrets Manager access
- **S3 Access**: Optional S3 permissions for application

### Load Balancing (alb.tf)
- **Application Load Balancer**: Internet-facing ALB in public subnets
- **Target Group**: IP-based targeting for Fargate tasks
- **Health Checks**: /healthz endpoint monitoring
- **Listeners**:
  - HTTP (80): Redirects to HTTPS
  - HTTPS (443): Forwards to target group (when SSL enabled)
- **CloudWatch Alarms**: Response time and unhealthy target monitoring

### Compute (ecs.tf)
- **ECS Cluster**: Fargate cluster with Container Insights
- **Task Definition**:
  - CPU: 512 (0.5 vCPU)
  - Memory: 1024 MB (1 GB)
  - Network Mode: awsvpc
  - Logging: CloudWatch Logs
- **ECS Service**:
  - Desired Count: 2 tasks
  - Launch Type: Fargate
  - Deployment: Circuit breaker with rollback
  - Execute Command: Enabled for debugging
- **Auto Scaling**:
  - Target Tracking: CPU (70%) and Memory (80%)
  - Min: 2 tasks
  - Max: 10 tasks

### Monitoring (monitoring.tf)
- **CloudWatch Dashboard**: ECS, ALB, and RDS metrics
- **SNS Topic**: Alarm notifications
- **CloudWatch Alarms**:
  - ECS CPU/Memory high utilization
  - ALB 5XX errors
  - RDS high connections
  - Database CPU and storage
- **Log Groups**: Application logs with configurable retention

### DNS & SSL (dns.tf)
- **Route53 Hosted Zone**: Optional new zone creation
- **ACM Certificate**: SSL/TLS certificate with automatic renewal
- **DNS Validation**: Automatic certificate validation
- **A Records**: Domain and www subdomain pointing to ALB

## Files Structure

```
terraform/
├── main.tf                    # Provider and backend configuration
├── variables.tf               # Input variables
├── outputs.tf                 # Output values
├── terraform.tfvars.example   # Example configuration
├── network.tf                 # VPC, subnets, routing
├── security_groups.tf         # Security group rules
├── rds.tf                     # PostgreSQL database
├── iam.tf                     # IAM roles and policies
├── alb.tf                     # Load balancer
├── ecs.tf                     # ECS cluster and service
├── monitoring.tf              # CloudWatch dashboards and alarms
├── dns.tf                     # Route53 and ACM
├── .gitignore                 # Git ignore rules
├── README.md                  # Deployment guide
└── INFRASTRUCTURE.md          # This file
```

## Key Features

### High Availability
- Multi-AZ deployment for load balancer
- Optional Multi-AZ for database
- Auto-scaling based on metrics
- Health checks and automatic replacement

### Security
- Private subnets for application and database
- Encrypted RDS storage
- Secrets Manager for credentials
- Security groups with least privilege
- No public database access
- HTTPS/TLS termination at ALB

### Observability
- Centralized CloudWatch logging
- Custom CloudWatch dashboard
- Comprehensive alarms
- ECS Container Insights
- RDS Enhanced Monitoring

### Scalability
- Auto-scaling based on CPU/Memory
- Fargate serverless compute
- RDS read replicas (can be added)
- CloudFront CDN (can be added)

### Cost Optimization
- Configurable instance sizes
- Optional NAT gateway
- Single-AZ option for dev
- Log retention policies
- Spot instances (can be configured)

## Environment Variables in ECS

The ECS task receives environment variables and secrets:

**Environment Variables:**
- `ENVIRONMENT`: Deployment environment (dev/staging/production)
- `ACCESS_TOKEN_EXPIRE_MINUTES`: JWT expiration time

**Secrets (from Secrets Manager):**
- `SECRET_KEY`: Application secret key
- `DATABASE_URL`: PostgreSQL connection string

## Estimated Costs

### Development (Minimal)
- ECS Fargate (1 task, 0.25 vCPU, 0.5 GB): ~$10/month
- RDS db.t4g.micro (Single-AZ): ~$15/month
- ALB: ~$20/month
- NAT Gateway (1): ~$33/month
- Misc (CloudWatch, data transfer): ~$5/month
- **Total: ~$83/month**

### Production (Recommended)
- ECS Fargate (2 tasks, 1 vCPU, 2 GB): ~$60/month
- RDS db.t4g.small (Multi-AZ): ~$60/month
- ALB: ~$20/month
- NAT Gateways (2): ~$65/month
- Misc (CloudWatch, data transfer): ~$10/month
- **Total: ~$215/month**

## Next Steps

1. Review and customize `terraform.tfvars`
2. Build and push Docker image to ECR
3. Run `terraform init` and `terraform apply`
4. Configure DNS (if using custom domain)
5. Set up monitoring alerts
6. Run database migrations
7. Test the deployment

## Maintenance Tasks

- **Weekly**: Review CloudWatch dashboards and alarms
- **Monthly**: Check for cost optimization opportunities
- **Quarterly**: Update Terraform providers and modules
- **As needed**: Rotate secrets in Secrets Manager
- **Before major changes**: Take RDS snapshots
