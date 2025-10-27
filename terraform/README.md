# PyShop API - Terraform Infrastructure

This directory contains Terraform configuration for deploying the PyShop API to AWS using ECS Fargate, RDS PostgreSQL, and supporting infrastructure.

## Architecture Overview

The infrastructure includes:

- **VPC & Networking**: Custom VPC with public/private subnets across 2 AZs
- **ECS Fargate**: Containerized application deployment with auto-scaling
- **Application Load Balancer**: HTTPS/HTTP traffic distribution
- **RDS PostgreSQL**: Managed database with automated backups
- **CloudWatch**: Centralized logging and monitoring with dashboards
- **Secrets Manager**: Secure storage for database credentials and app secrets
- **Route53 & ACM**: DNS management and SSL/TLS certificates (optional)
- **IAM**: Least-privilege roles for ECS tasks

## Prerequisites

1. **AWS Account** with appropriate permissions
2. **Terraform** >= 1.0 ([Install](https://www.terraform.io/downloads))
3. **AWS CLI** configured with credentials ([Install](https://aws.amazon.com/cli/))
4. **Docker image** of your application pushed to ECR or Docker Hub

## Cost Optimization

**This infrastructure includes cost-saving features that can reduce monthly costs by up to 80%.**

See [COST_OPTIMIZATION.md](COST_OPTIMIZATION.md) for detailed cost-saving strategies.

### Quick Cost Comparison:
- **Original configuration**: ~$215/month
- **Cost-optimized**: ~$35-45/month (83% savings)
- **Key features**: Fargate Spot (70% off), single NAT gateway, minimal resources

**Ready-to-use configs:**
- `ultra-low-cost.tfvars.example` - Development (~$35-45/month)
- `dev.tfvars.example` - Development/Staging (~$50/month)
- `production.tfvars.example` - Production (~$150/month)

## Quick Start

### 1. Configure AWS Credentials

```bash
aws configure
# Enter your AWS Access Key ID, Secret Access Key, and region
```

### 2. Create ECR Repository and Push Image

```bash
# Create ECR repository
aws ecr create-repository --repository-name pyshop-api --region us-east-1

# Authenticate Docker to ECR
aws ecr get-login-password --region us-east-1 | docker login --username AWS --password-stdin <account-id>.dkr.ecr.us-east-1.amazonaws.com

# Build and tag the image
cd .. # Go to project root
docker build -t pyshop-api:latest .
docker tag pyshop-api:latest <account-id>.dkr.ecr.us-east-1.amazonaws.com/pyshop-api:latest

# Push to ECR
docker push <account-id>.dkr.ecr.us-east-1.amazonaws.com/pyshop-api:latest
```

### 3. Configure Terraform Variables

```bash
cd terraform
cp terraform.tfvars.example terraform.tfvars
```

Edit `terraform.tfvars` with your configuration:

```hcl
project_name = "pyshop"
environment  = "dev"
aws_region   = "us-east-1"

# Update with your ECR image URI
app_image = "<account-id>.dkr.ecr.us-east-1.amazonaws.com/pyshop-api:latest"

# For SSL/HTTPS (optional)
enable_ssl  = true
domain_name = "api.yourdomain.com"
```

### 4. Deploy Infrastructure

```bash
# Initialize Terraform
terraform init

# Review the execution plan
terraform plan

# Deploy infrastructure
terraform apply
```

The deployment takes approximately 10-15 minutes.

### 5. Access Your Application

After deployment:

```bash
# Get the ALB URL
terraform output alb_url

# Test the API
curl $(terraform output -raw alb_url)/healthz
```

## Configuration

### Environment-Specific Deployments

Use Terraform workspaces for multiple environments:

```bash
# Create and switch to production workspace
terraform workspace new production
terraform workspace select production

# Deploy with production-specific tfvars
terraform apply -var-file="production.tfvars"
```

### SSL/TLS Setup

To enable HTTPS:

1. Set `enable_ssl = true` in `terraform.tfvars`
2. Provide your `domain_name`
3. Choose one of:
   - **New Route53 zone**: Set `create_route53_zone = true`
   - **Existing zone**: Set `route53_zone_id = "Z1234567890ABC"`

After deployment, update your domain's nameservers (if new zone):

```bash
terraform output route53_name_servers
```

### Database Access

Database credentials are stored in AWS Secrets Manager:

```bash
# Get database secret ARN
terraform output db_secrets_arn

# Retrieve credentials
aws secretsmanager get-secret-value --secret-id <secret-arn> --query SecretString --output text | jq
```

### Auto Scaling

The ECS service auto-scales based on:
- **CPU**: Scales out at 70% average utilization
- **Memory**: Scales out at 80% average utilization
- **Range**: 2-10 tasks (configurable via `autoscaling_min/max_capacity`)

### Cost Optimization

For development environments:

```hcl
# terraform.tfvars
enable_nat_gateway   = false  # Use if ECS tasks don't need internet
db_multi_az         = false   # Single AZ for dev
db_instance_class   = "db.t4g.micro"
fargate_cpu         = "256"
fargate_memory      = "512"
app_count           = 1
```

For production:

```hcl
enable_nat_gateway   = true
db_multi_az         = true
db_instance_class   = "db.t4g.small"
fargate_cpu         = "1024"
fargate_memory      = "2048"
app_count           = 2
```

## Monitoring & Observability

### CloudWatch Dashboard

Access the dashboard:
```bash
aws cloudwatch get-dashboard --dashboard-name $(terraform output -raw cloudwatch_dashboard_name)
```

Or visit: AWS Console → CloudWatch → Dashboards

### Logs

View application logs:
```bash
aws logs tail /ecs/pyshop-dev --follow
```

### Alarms

SNS topic for alarms:
```bash
terraform output sns_alarms_topic_arn

# Subscribe to email notifications
aws sns subscribe --topic-arn <arn> --protocol email --notification-endpoint your@email.com
```

## Maintenance

### Updating the Application

```bash
# Build and push new image
docker build -t pyshop-api:latest .
docker tag pyshop-api:latest <ecr-uri>:latest
docker push <ecr-uri>:latest

# Force new deployment (ECS will pull latest image)
aws ecs update-service \
  --cluster $(terraform output -raw ecs_cluster_name) \
  --service $(terraform output -raw ecs_service_name) \
  --force-new-deployment
```

### Database Migrations

Connect via ECS Exec:

```bash
# Enable execute command (already enabled in terraform)
aws ecs execute-command \
  --cluster $(terraform output -raw ecs_cluster_name) \
  --task <task-id> \
  --container pyshop-app \
  --interactive \
  --command "/bin/sh"

# Inside container, run migrations
alembic upgrade head
```

### Backup & Disaster Recovery

**Automated Backups**: RDS automatically backs up with 7-day retention

**Manual Snapshot**:
```bash
aws rds create-db-snapshot \
  --db-instance-identifier $(terraform output -raw db_instance_identifier) \
  --db-snapshot-identifier pyshop-manual-snapshot-$(date +%Y%m%d)
```

**Restore from Snapshot**:
```bash
aws rds restore-db-instance-from-db-snapshot \
  --db-instance-identifier pyshop-restored \
  --db-snapshot-identifier <snapshot-id>
```

## Remote State (Recommended for Teams)

Configure S3 backend in `main.tf`:

```hcl
terraform {
  backend "s3" {
    bucket         = "your-terraform-state-bucket"
    key            = "pyshop/terraform.tfstate"
    region         = "us-east-1"
    encrypt        = true
    dynamodb_table = "terraform-state-lock"
  }
}
```

Create resources:
```bash
# Create S3 bucket
aws s3 mb s3://your-terraform-state-bucket --region us-east-1
aws s3api put-bucket-versioning --bucket your-terraform-state-bucket --versioning-configuration Status=Enabled

# Create DynamoDB table for locking
aws dynamodb create-table \
  --table-name terraform-state-lock \
  --attribute-definitions AttributeName=LockID,AttributeType=S \
  --key-schema AttributeName=LockID,KeyType=HASH \
  --billing-mode PAY_PER_REQUEST
```

## Troubleshooting

### ECS Tasks Failing

Check logs:
```bash
aws logs tail /ecs/pyshop-dev --follow --filter-pattern "ERROR"
```

Check task status:
```bash
aws ecs describe-tasks \
  --cluster $(terraform output -raw ecs_cluster_name) \
  --tasks <task-id>
```

### Database Connection Issues

1. Verify security groups allow traffic
2. Check secrets are correctly populated
3. Test connectivity from ECS task:

```bash
aws ecs execute-command \
  --cluster $(terraform output -raw ecs_cluster_name) \
  --task <task-id> \
  --container pyshop-app \
  --interactive \
  --command "/bin/sh"

# Inside container
nc -zv <db-endpoint> 5432
```

### ALB Health Checks Failing

Ensure `/healthz` endpoint returns 200:
```bash
curl -v http://<alb-dns>/healthz
```

## Cleanup

To destroy all infrastructure:

```bash
# Review what will be deleted
terraform plan -destroy

# Destroy infrastructure
terraform destroy
```

**Warning**: This will delete:
- Database (unless `deletion_protection = true`)
- All logs (unless explicitly configured otherwise)
- All secrets (after 7-day recovery window)

## Security Best Practices

1. **Enable deletion protection** for production databases
2. **Use Multi-AZ** deployment for production RDS
3. **Enable VPC Flow Logs** for network monitoring
4. **Rotate secrets** regularly via Secrets Manager
5. **Use IAM roles** instead of access keys
6. **Enable AWS CloudTrail** for audit logging
7. **Review security group rules** periodically
8. **Enable GuardDuty** for threat detection

## Cost Estimation

### Ultra Low Cost Configuration (~$35-45/month)
Uses: Fargate Spot, single NAT, minimal resources

| Resource | Configuration | Monthly Cost |
|----------|--------------|--------------|
| ECS Fargate Spot (1 task) | 0.25 vCPU, 0.5GB RAM | ~$2.50 |
| RDS db.t4g.micro | Single-AZ, 20GB | ~$12 |
| Application Load Balancer | Standard | ~$20 |
| NAT Gateway (1 AZ) | Standard | ~$33 |
| VPC Endpoints (5) | Interface endpoints | ~$7 |
| CloudWatch Logs | Minimal | ~$1 |
| Data Transfer | ~50GB/month | ~$2 |
| **Total** | | **~$77.50/month** |

### Standard Production (~$150-200/month)
Uses: Mix of Spot/On-demand, HA setup

| Resource | Configuration | Monthly Cost |
|----------|--------------|--------------|
| ECS Fargate (70% Spot) | 3 tasks, 1 vCPU, 2GB | ~$60 |
| RDS db.t4g.small | Multi-AZ | ~$60 |
| Application Load Balancer | Standard | ~$20 |
| NAT Gateways (2 AZs) | High availability | ~$65 |
| VPC Endpoints | Interface endpoints | ~$7 |
| CloudWatch | Logs + Metrics | ~$5 |
| Data Transfer | ~200GB/month | ~$10 |
| **Total** | | **~$227/month** |

**Save even more:**
- Use VPC endpoints + disable NAT: Save $26-59/month
- 100% Fargate Spot: Save additional 70% on compute
- Aurora Serverless v2 with low traffic: Varies based on usage

## Support

For issues or questions:
- Terraform Registry: https://registry.terraform.io/
- AWS Documentation: https://docs.aws.amazon.com/
- Project Repository: [Add your repo URL]

## License

[Add your license information]
