# Cost Optimization Guide

This guide explains the cost-saving features and configurations available in the Terraform infrastructure.

## Cost Breakdown

### Original Configuration (~$215/month)
- ECS Fargate (2 tasks, 1 vCPU, 2 GB): ~$60/month
- RDS db.t4g.small (Multi-AZ): ~$60/month
- Application Load Balancer: ~$20/month
- NAT Gateways (2): ~$65/month
- Misc (CloudWatch, data transfer): ~$10/month

### Optimized Configuration (~$35-45/month)
- ECS Fargate Spot (1 task, 0.25 vCPU, 0.5 GB): ~$2.50/month
- RDS db.t4g.micro (Single-AZ): ~$12/month
- Application Load Balancer: ~$20/month
- NAT Gateway (1): ~$33/month
- VPC Endpoints (5): ~$7/month
- Misc: ~$3/month

**Savings: ~$170/month (79% reduction)**

## Cost Optimization Features

### 1. Single NAT Gateway (Saves ~$33/month)

```hcl
enable_nat_gateway = true
single_nat_gateway = true  # Use one NAT instead of one per AZ
```

**Trade-offs:**
- ✅ 50% cost reduction on NAT
- ❌ Not highly available (single point of failure)
- ✅ Good for dev/staging environments

### 2. VPC Endpoints (Saves data transfer costs)

```hcl
enable_vpc_endpoints = true  # Adds ~$7/month, saves on data transfer
```

**What it does:**
- Gateway endpoints (S3, DynamoDB): FREE
- Interface endpoints: $7.30/month per endpoint
- Data processing: $0.01/GB (vs NAT $0.045/GB)

**Break-even:** ~117 GB/month data transfer

**Endpoints included:**
- S3 (Gateway - FREE)
- DynamoDB (Gateway - FREE)
- ECR API (Interface - for pulling images)
- ECR Docker (Interface - for pulling images)
- CloudWatch Logs (Interface - for logging)
- Secrets Manager (Interface - for credentials)

### 3. Fargate Spot (Saves 70% on compute)

```hcl
enable_fargate_spot = true
fargate_spot_weight = 100  # 100% Spot for maximum savings
fargate_base_tasks  = 0    # No guaranteed on-demand tasks
```

**Cost comparison:**
- Regular Fargate (0.25 vCPU, 0.5 GB): ~$8.50/month per task
- Fargate Spot (0.25 vCPU, 0.5 GB): ~$2.50/month per task

**Trade-offs:**
- ✅ 70% cost reduction
- ❌ May be interrupted (rarely happens)
- ❌ 2-minute interruption warning
- ✅ Good for stateless applications

**Best practices:**
- Use 100% Spot for dev/staging
- Production: 70-80% Spot + 20-30% on-demand base
- Ensure graceful shutdown handling

### 4. Smaller Fargate Tasks

```hcl
fargate_cpu    = "256"  # 0.25 vCPU (vs 1 vCPU)
fargate_memory = "512"  # 0.5 GB (vs 2 GB)
```

**Cost impact:**
- 0.25 vCPU, 0.5 GB: $0.01188/hour = $8.50/month
- 1 vCPU, 2 GB: $0.08365/hour = $60/month

**Savings: ~$51.50/month per task**

### 5. RDS vs Aurora Serverless v2

#### RDS (Best for constant low traffic)
```hcl
use_aurora_serverless = false
db_instance_class     = "db.t4g.micro"  # ~$12/month
```

#### Aurora Serverless v2 (Best for variable traffic)
```hcl
use_aurora_serverless = true
aurora_min_capacity   = 0.5  # ~$43/month if always on
aurora_max_capacity   = 2.0
```

**When to use each:**
- **RDS t4g.micro**: Constant, low traffic ($12/month)
- **Aurora Serverless v2**: Variable workloads, burst capacity

### 6. Reduced Auto-Scaling

```hcl
autoscaling_min_capacity = 1  # Start with 1 task
autoscaling_max_capacity = 4  # Scale up to 4 (vs 10)
```

**Cost impact:** Prevents over-scaling during traffic spikes

### 7. Shorter Log Retention

```hcl
log_retention_days = 3  # vs 7 or 30 days
```

**Savings:** ~$1-5/month depending on log volume

## Cost Optimization Strategies

### Strategy 1: Ultra Low Cost Dev/Staging (~$35-45/month)

```hcl
# Network
single_nat_gateway   = true
enable_vpc_endpoints = true

# Compute
app_count           = 1
fargate_cpu         = "256"
fargate_memory      = "512"
enable_fargate_spot = true
fargate_spot_weight = 100

# Database
use_aurora_serverless = false
db_instance_class     = "db.t4g.micro"
db_multi_az           = false

# Scaling
autoscaling_min_capacity = 1
autoscaling_max_capacity = 2
```

**Use case:** Development, staging, proof-of-concept

### Strategy 2: Cost-Effective Production (~$80-100/month)

```hcl
# Network
single_nat_gateway   = true  # Or false for HA
enable_vpc_endpoints = true

# Compute
app_count           = 2
fargate_cpu         = "512"
fargate_memory      = "1024"
enable_fargate_spot = true
fargate_spot_weight = 70      # 70% Spot, 30% on-demand
fargate_base_tasks  = 1       # Always 1 on-demand

# Database
use_aurora_serverless = false
db_instance_class     = "db.t4g.small"
db_multi_az           = true  # For HA

# Scaling
autoscaling_min_capacity = 2
autoscaling_max_capacity = 6
```

**Use case:** Small production workloads with HA

### Strategy 3: High Performance (~$150-200/month)

```hcl
# Network
single_nat_gateway   = false  # Multi-AZ NAT for HA
enable_vpc_endpoints = true

# Compute
app_count           = 3
fargate_cpu         = "1024"
fargate_memory      = "2048"
enable_fargate_spot = true
fargate_spot_weight = 50
fargate_base_tasks  = 2

# Database
use_aurora_serverless = true  # For better scaling
aurora_min_capacity   = 1.0
aurora_max_capacity   = 4.0
# OR
db_instance_class = "db.t4g.medium"
db_multi_az       = true

# Scaling
autoscaling_min_capacity = 3
autoscaling_max_capacity = 10
```

**Use case:** Production with significant traffic

## Alternative Architectures

### Option 1: Remove NAT Gateway (Saves $33/month)

If your application only needs to access AWS services:

```hcl
enable_nat_gateway   = false
enable_vpc_endpoints = true  # Required for AWS service access
```

**Requirements:**
- No external API calls
- All dependencies via VPC endpoints
- S3, ECR, CloudWatch, Secrets Manager via endpoints

### Option 2: AWS App Runner (Cheapest for simple apps)

Consider using AWS App Runner instead:
- ~$25/month total for small workloads
- Includes load balancer, compute, and auto-scaling
- No NAT gateway needed
- Limited customization vs ECS

### Option 3: Lambda + API Gateway (Serverless)

For very low traffic:
- Pay per request
- No idle costs
- Cold starts may be an issue
- ~$5-20/month for low traffic

## Monitoring Costs

### CloudWatch Costs
- Logs: $0.50/GB ingested + $0.03/GB stored
- Metrics: First 10,000 free, then $0.30 per 1,000
- Dashboards: $3/month per dashboard

**Optimization:**
- Use shorter retention periods
- Filter logs to reduce ingestion
- Use log insights sparingly

### Data Transfer Costs
- NAT Gateway: $0.045/GB
- VPC Endpoint: $0.01/GB
- Internet egress: $0.09/GB (first 10TB)

**Optimization:**
- Use VPC endpoints for AWS services
- Cache static content in CloudFront
- Compress API responses

## Cost Monitoring Tools

### 1. AWS Cost Explorer
```bash
# Enable in AWS Console
aws ce get-cost-and-usage \
  --time-period Start=2024-01-01,End=2024-01-31 \
  --granularity MONTHLY \
  --metrics BlendedCost
```

### 2. AWS Budgets
Create a budget alert:
```bash
aws budgets create-budget \
  --account-id 123456789012 \
  --budget file://budget.json \
  --notifications file://notifications.json
```

### 3. Terraform Cost Estimation
Use Infracost for Terraform:
```bash
brew install infracost
infracost breakdown --path .
```

## Best Practices

1. **Start small, scale up**
   - Begin with minimal resources
   - Monitor performance
   - Scale based on actual needs

2. **Use Spot instances for non-critical workloads**
   - Dev/staging: 100% Spot
   - Production: 70-80% Spot

3. **Right-size your resources**
   - Monitor CPU/Memory usage
   - Adjust Fargate task sizes accordingly
   - Use auto-scaling effectively

4. **Leverage free tier**
   - 750 hours of ALB per month (first year)
   - 25 GB CloudWatch Logs (always free)
   - 10 custom CloudWatch metrics

5. **Review costs regularly**
   - Set up billing alerts
   - Review Cost Explorer monthly
   - Identify unused resources

6. **Use Reserved Instances for stable workloads**
   - 1-year commitment: 30-40% savings
   - 3-year commitment: 50-60% savings

## Quick Cost Comparison

| Configuration | Monthly Cost | Use Case |
|--------------|--------------|----------|
| Original (High Performance) | $215 | Production, high traffic |
| Cost-Optimized Production | $80-100 | Production, moderate traffic |
| Ultra Low Cost | $35-45 | Dev/Staging |
| Minimal (no NAT) | $25-35 | Dev/Test with VPC endpoints only |
| AWS App Runner | $20-30 | Simple apps, low traffic |

## Action Items

1. ✅ Review your traffic patterns
2. ✅ Choose appropriate configuration
3. ✅ Update `terraform.tfvars` with cost-optimized values
4. ✅ Set up billing alerts
5. ✅ Monitor for 1-2 weeks
6. ✅ Adjust based on actual usage

## Need Help?

- Review AWS Cost Optimization Pillar: https://docs.aws.amazon.com/wellarchitected/
- Use AWS Pricing Calculator: https://calculator.aws/
- Contact AWS Support for cost optimization review
