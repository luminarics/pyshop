# Azure Cost Optimization Guide for PyShop API

This guide provides strategies to minimize Azure costs while maintaining functionality and reliability.

## Cost Breakdown

### Development Environment (~$30-50/month)

| Resource | Configuration | Monthly Cost (Estimate) |
|----------|--------------|-------------------------|
| Container Apps | 0.25 vCPU, 0.5GB RAM, 1 replica | ~$15-20 |
| PostgreSQL Flexible Server | B_Standard_B1ms, 32GB | ~$12 |
| Azure Container Registry | Basic tier | ~$5 |
| Log Analytics | 5GB ingestion | ~$2 |
| Application Insights | Standard tier | ~$0-5 |
| Virtual Network | Standard VNet | ~$0 |
| Key Vault | Standard tier | ~$0.03 |
| **Total** | | **~$34-44/month** |

### Production Environment (~$150-300/month)

| Resource | Configuration | Monthly Cost (Estimate) |
|----------|--------------|-------------------------|
| Container Apps | 1 vCPU, 2GB RAM, 2-4 replicas | ~$60-120 |
| PostgreSQL Flexible Server | GP_Standard_D2s_v3, 128GB, HA | ~$150-200 |
| Azure Container Registry | Standard tier | ~$20 |
| Log Analytics | 20GB ingestion | ~$10 |
| Application Insights | Standard tier | ~$5-10 |
| Virtual Network | Standard VNet | ~$0 |
| Key Vault | Standard tier | ~$0.03 |
| Network Security Groups | Standard | ~$0 |
| **Total (without DDoS)** | | **~$245-360/month** |
| **DDoS Protection Standard** | If enabled | **+$2,900/month** |

## Cost Optimization Strategies

### 1. Database Optimization

#### Use Burstable Tier for Development
```hcl
# dev.tfvars
postgres_sku_name = "B_Standard_B1ms"  # ~$12/month vs ~$150/month for GP tier
postgres_storage_mb = 32768            # Only what you need
postgres_high_availability = false     # Single zone for dev
postgres_geo_redundant_backup = false  # Local backups only
```

**Savings**: ~$138/month for development environments

#### Optimize Production Database
```hcl
# production.tfvars
postgres_sku_name = "GP_Standard_D2ds_v4"  # Newer generation, better price/performance
postgres_storage_mb = 65536                # Start smaller, scale as needed
postgres_backup_retention_days = 7         # Reduce if 7 days is sufficient
```

**Savings**: Up to $50/month with right-sized SKU

#### Consider Azure Cosmos DB for PostgreSQL (Citus)
For very low traffic applications, Cosmos DB with serverless billing might be cheaper, but typically PostgreSQL Flexible Server is more cost-effective for consistent workloads.

### 2. Container Apps Optimization

#### Right-Size Your Containers
```hcl
# Start small and scale up if needed
app_cpu = "0.25"      # Quarter vCPU
app_memory = "0.5Gi"  # 512MB RAM
```

**Savings**: ~$40-60/month compared to 1 vCPU, 2GB configuration

#### Optimize Scaling Settings
```hcl
app_min_replicas = 0  # Scale to zero when not in use (dev only)
app_max_replicas = 3  # Limit maximum instances
```

**Important**: Scaling to 0 replicas means cold starts. Only use for dev/test environments.

**Savings**: ~$15-30/month for development environments with low traffic

#### Use Consumption Plan Wisely
Container Apps pricing:
- **vCPU**: $0.000024/vCPU-second
- **Memory**: $0.000004/GB-second
- **Requests**: $0.40 per million requests

Calculate your costs:
- 1 replica at 0.5 vCPU, 1GB RAM running 24/7: ~$15-20/month
- 2 replicas at 1 vCPU, 2GB RAM running 24/7: ~$60-80/month

### 3. Container Registry Optimization

#### Use Basic Tier
```hcl
acr_sku = "Basic"  # $5/month vs $20/month for Standard
```

**When to upgrade to Standard**:
- Need webhooks for CI/CD integration
- Require geo-replication
- Need higher storage or bandwidth

**Savings**: $15/month

### 4. Logging and Monitoring Optimization

#### Reduce Log Retention
```hcl
log_retention_days = 30  # vs 90 or 180 days
```

**Savings**: ~$5-20/month depending on log volume

#### Optimize Log Ingestion
```hcl
# In your application, reduce log verbosity in production
# Only log INFO and above, not DEBUG
```

**Savings**: ~$10-50/month for high-traffic applications

#### Use Sampling in Application Insights
In your Python code:
```python
# Reduce telemetry sampling
from applicationinsights.channel import TelemetryChannel, SamplingTelemetryProcessor

channel = TelemetryChannel()
processor = SamplingTelemetryProcessor(0.1)  # 10% sampling
channel.telemetry_processor_chain.append(processor)
```

**Savings**: ~$5-15/month

### 5. Network Optimization

#### Avoid DDoS Protection Standard Unless Required
```hcl
enable_ddos_protection = false  # Save $2,900/month!
```

**When you need it**:
- Regulatory requirements
- High-value production applications
- History of DDoS attacks

**Alternative**: Use Azure Front Door or Application Gateway WAF for basic DDoS protection (~$35-100/month)

#### Use Service Endpoints Instead of Private Endpoints
For non-sensitive workloads, service endpoints are free while private endpoints cost ~$7-10/month each.

**Savings**: ~$20-30/month

### 6. Regional Selection

Choose cost-effective regions:
- **East US**: Typically lowest cost
- **West US 2**: Good balance of cost and features
- **Avoid premium regions**: North Europe, West Europe can be 10-20% more expensive

**Savings**: ~5-15% total infrastructure cost

## Ultra Low-Cost Configuration (~$25-35/month)

For side projects or learning:

```hcl
# ultra-low-cost.tfvars
project_name = "pyshop"
environment  = "dev"
location     = "eastus"

# Minimal database
postgres_sku_name = "B_Standard_B1ms"
postgres_storage_mb = 32768
postgres_backup_retention_days = 7
postgres_geo_redundant_backup = false
postgres_high_availability = false

# Scale-to-zero container apps
use_container_apps = true
app_cpu = "0.25"
app_memory = "0.5Gi"
app_min_replicas = 0  # Scale to zero!
app_max_replicas = 2

# Basic registry
acr_sku = "Basic"

# Minimal logging
log_retention_days = 7

# Wide open security (dev only!)
allowed_ip_ranges = ["0.0.0.0/0"]
enable_ddos_protection = false
```

**Total**: ~$25-35/month

**Trade-offs**:
- Cold starts (scale from zero)
- No high availability
- Minimal logging retention
- Single region
- No geo-redundant backups

## Reserved Instances & Savings Plans

### Azure Database Reservations
Reserve PostgreSQL capacity for 1-3 years:
- **1 year**: ~15% savings
- **3 years**: ~30-40% savings

```bash
# Purchase reservation via Azure Portal or CLI
az postgres flexible-server reservation create \
  --name pyshop-db-reservation \
  --sku-name GP_Standard_D2s_v3 \
  --tier GeneralPurpose \
  --capacity 2 \
  --term P1Y  # 1 year
```

### Azure Savings Plans
Commit to a hourly spend for 1-3 years:
- **1 year**: ~15-20% savings
- **3 years**: ~25-30% savings

**Best for**: Stable, predictable workloads

## Cost Monitoring and Alerts

### Set Up Budget Alerts

```bash
# Create a budget for the resource group
az consumption budget create \
  --budget-name pyshop-monthly-budget \
  --amount 100 \
  --time-grain Monthly \
  --start-date 2024-01-01 \
  --resource-group $(terraform output -raw resource_group_name) \
  --notifications \
    threshold=80 \
    contact-emails=["your@email.com"] \
    enabled=true
```

### Monitor Costs Daily

```bash
# View current month costs
az consumption usage list \
  --start-date $(date -u -d "first day of this month" +%Y-%m-%d) \
  --end-date $(date -u +%Y-%m-%d) \
  --output table
```

### Use Azure Cost Management

1. Navigate to: Azure Portal → Cost Management + Billing
2. Enable cost analysis and recommendations
3. Set up anomaly detection alerts

## Cost Optimization Checklist

- [ ] Right-size database SKU for your workload
- [ ] Use Burstable tier for dev/test databases
- [ ] Disable high availability for non-production environments
- [ ] Configure container apps to scale to zero for dev environments
- [ ] Use Basic ACR tier unless you need advanced features
- [ ] Reduce log retention to minimum required period
- [ ] Avoid DDoS Protection Standard unless absolutely required
- [ ] Choose cost-effective Azure regions (East US, Central US)
- [ ] Delete unused resources regularly
- [ ] Set up cost alerts and budgets
- [ ] Review Azure Advisor recommendations monthly
- [ ] Consider reservations for production workloads
- [ ] Use tags to track costs by project/environment

## Common Cost Mistakes to Avoid

1. **Leaving DDoS Protection enabled** (~$2,900/month waste)
2. **Over-provisioning database** (use monitoring to right-size)
3. **Not scaling to zero in dev** (save ~$15-20/month per environment)
4. **Excessive log retention** (90+ days when 30 is sufficient)
5. **Multiple NAT Gateways** (not needed for this architecture)
6. **Unused resources** (delete test resources promptly)
7. **Premium regions** (West Europe vs East US = 15% more cost)
8. **Not using reserved instances** for production (miss 30-40% savings)

## Summary

| Environment | Configuration | Monthly Cost | Best For |
|-------------|--------------|--------------|----------|
| **Ultra Low Cost** | B1ms DB, 0.25 vCPU app, scale-to-zero | $25-35 | Learning, side projects |
| **Development** | B1ms DB, 0.5 vCPU app, 1 replica | $34-44 | Active development |
| **Staging** | B2s DB, 1 vCPU app, 1-2 replicas | $60-80 | Pre-production testing |
| **Production (Basic)** | D2s DB, 1-2 vCPU app, 2-4 replicas | $150-250 | Small production apps |
| **Production (HA)** | D4s DB HA, 2 vCPU app, 4-10 replicas | $300-500 | High-traffic apps |

**Key Takeaway**: You can run a fully functional PyShop API deployment for as little as $25-35/month for development, or $150-250/month for a production setup with reasonable scaling.
