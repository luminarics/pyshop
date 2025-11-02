# PyShop API - Azure Terraform Infrastructure

This directory contains Terraform configuration for deploying the PyShop API to Microsoft Azure using Container Apps, Azure Database for PostgreSQL, and supporting infrastructure.

## Architecture Overview

The infrastructure includes:

- **Virtual Network**: Custom VNet with dedicated subnets for app and database
- **Azure Container Apps**: Serverless container hosting with auto-scaling (recommended)
  - Alternative: Azure App Service for Web Apps
- **Azure Container Registry (ACR)**: Private Docker image registry
- **Azure Database for PostgreSQL**: Managed database with automated backups
- **Application Insights**: APM and distributed tracing
- **Log Analytics**: Centralized logging and monitoring
- **Key Vault**: Secure storage for secrets and connection strings
- **Network Security Groups**: Network-level security controls

## Prerequisites

1. **Azure Account** with an active subscription
2. **Azure CLI** installed and configured ([Install](https://learn.microsoft.com/en-us/cli/azure/install-azure-cli))
3. **Terraform** >= 1.0 ([Install](https://developer.hashicorp.com/terraform/install))
4. **Docker** for building and pushing images ([Install](https://docs.docker.com/get-docker/))

## Quick Start

### 1. Authenticate to Azure

```bash
# Login to Azure
az login

# Set your subscription (if you have multiple)
az account set --subscription "your-subscription-id"

# Verify current subscription
az account show
```

### 2. Create Azure Container Registry and Push Image

```bash
# Note: You can create ACR via Terraform, but you need to push the initial image first

# Build the Docker image
cd .. # Go to project root
docker build -t pyshop-api:latest .

# The ACR will be created by Terraform, so wait until after 'terraform apply'
# Then tag and push your image:
# docker tag pyshop-api:latest <acr-name>.azurecr.io/pyshop-api:latest
# az acr login --name <acr-name>
# docker push <acr-name>.azurecr.io/pyshop-api:latest
```

### 3. Configure Terraform Variables

```bash
cd terraform-azure
cp terraform.tfvars.example terraform.tfvars
```

Edit `terraform.tfvars` with your configuration:

```hcl
project_name = "pyshop"
environment  = "dev"
location     = "eastus"

# Database configuration
postgres_sku_name = "B_Standard_B1ms"  # For dev

# Container Apps configuration
use_container_apps = true
app_cpu           = "0.5"
app_memory        = "1Gi"
app_min_replicas  = 1
app_max_replicas  = 10

# Optional: Set your secret key (or leave empty to auto-generate)
secret_key = "your-super-secret-key-here"
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

### 5. Push Your Container Image

After Terraform creates the infrastructure:

```bash
# Get ACR details
ACR_NAME=$(terraform output -raw container_registry_name)
ACR_LOGIN_SERVER=$(terraform output -raw container_registry_login_server)

# Login to ACR
az acr login --name $ACR_NAME

# Tag and push your image
docker tag pyshop-api:latest $ACR_LOGIN_SERVER/pyshop-api:latest
docker push $ACR_LOGIN_SERVER/pyshop-api:latest

# If using Container Apps, trigger a new revision
az containerapp update \
  --name $(terraform output -raw container_app_name) \
  --resource-group $(terraform output -raw resource_group_name) \
  --image $ACR_LOGIN_SERVER/pyshop-api:latest
```

### 6. Access Your Application

```bash
# Get the application URL
terraform output container_app_url

# Test the API
curl $(terraform output -raw container_app_url)/healthz
```

## Configuration

### Environment-Specific Deployments

Use Terraform workspaces or separate tfvars files:

```bash
# Using workspaces
terraform workspace new production
terraform workspace select production
terraform apply -var-file="production.tfvars"

# Or simply use different tfvars files
terraform apply -var-file="dev.tfvars"
terraform apply -var-file="production.tfvars"
```

### Container Apps vs App Service

**Container Apps (Recommended)**:
- Serverless, pay-per-use pricing
- Built-in auto-scaling
- Integrated with KEDA for advanced scaling
- Microservices-friendly
- Set `use_container_apps = true`

**App Service**:
- Traditional PaaS offering
- Always-on instances
- Better for legacy apps or specific features
- Set `use_container_apps = false`

### Database Access

Database credentials are stored in Azure Key Vault:

```bash
# Get Key Vault name
KV_NAME=$(terraform output -raw key_vault_name)

# Retrieve database password
az keyvault secret show --vault-name $KV_NAME --name postgres-password --query value -o tsv

# Get full connection string
az keyvault secret show --vault-name $KV_NAME --name database-url --query value -o tsv
```

### Auto Scaling

**Container Apps** auto-scales based on:
- **HTTP requests**: Scales at 100 concurrent requests per instance
- **CPU/Memory**: Can add custom scaling rules
- **Range**: Configurable via `app_min_replicas` and `app_max_replicas`

To add custom scaling rules, modify `container_apps.tf`:

```hcl
cpu_scale_rule {
  name                = "cpu-rule"
  cpu_utilization_percentage = 70
}
```

## Monitoring & Observability

### Application Insights

Access Application Insights in Azure Portal:

```bash
# Get Application Insights details
az monitor app-insights component show \
  --app $(terraform output -raw resource_group_name) \
  --resource-group $(terraform output -raw resource_group_name)
```

Or visit: Azure Portal → Application Insights → [your-app-name]

### Logs

View container logs:

```bash
# Container Apps logs
az containerapp logs show \
  --name $(terraform output -raw container_app_name) \
  --resource-group $(terraform output -raw resource_group_name) \
  --follow

# Or use Log Analytics
az monitor log-analytics query \
  --workspace $(terraform output -raw resource_group_name) \
  --analytics-query "ContainerAppConsoleLogs_CL | where TimeGenerated > ago(1h)"
```

### Alerts

Monitor alerts in the Action Group:

```bash
# List action groups
az monitor action-group list \
  --resource-group $(terraform output -raw resource_group_name)

# Add email notification
az monitor action-group update \
  --name pyshop-dev-action-group \
  --resource-group $(terraform output -raw resource_group_name) \
  --add-action email your-email your@email.com
```

## Maintenance

### Updating the Application

```bash
# Build new image
docker build -t pyshop-api:latest .

# Push to ACR
ACR_LOGIN_SERVER=$(terraform output -raw container_registry_login_server)
docker tag pyshop-api:latest $ACR_LOGIN_SERVER/pyshop-api:latest
az acr login --name $(terraform output -raw container_registry_name)
docker push $ACR_LOGIN_SERVER/pyshop-api:latest

# Update Container App (it will auto-deploy the new image)
az containerapp update \
  --name $(terraform output -raw container_app_name) \
  --resource-group $(terraform output -raw resource_group_name) \
  --image $ACR_LOGIN_SERVER/pyshop-api:latest
```

### Database Migrations

Run migrations from your local machine or CI/CD:

```bash
# Get database connection details
DB_HOST=$(terraform output -raw postgres_server_fqdn)
DB_PASSWORD=$(az keyvault secret show \
  --vault-name $(terraform output -raw key_vault_name) \
  --name postgres-password \
  --query value -o tsv)

# Set environment variable
export DATABASE_URL="postgresql+asyncpg://psqladmin:$DB_PASSWORD@$DB_HOST:5432/fastapi"

# Run migrations
poetry run alembic upgrade head
```

Or execute from a container:

```bash
# Execute command in running container
az containerapp exec \
  --name $(terraform output -raw container_app_name) \
  --resource-group $(terraform output -raw resource_group_name) \
  --command "alembic upgrade head"
```

### Backup & Disaster Recovery

**Automated Backups**: PostgreSQL Flexible Server automatically backs up with configurable retention (7-35 days)

**Manual Backup**:
```bash
# Not directly available for Flexible Server
# Use point-in-time restore instead
```

**Point-in-Time Restore**:
```bash
# Restore to a specific point in time
az postgres flexible-server restore \
  --resource-group $(terraform output -raw resource_group_name) \
  --name pyshop-restored-$(date +%Y%m%d) \
  --source-server $(terraform output -raw postgres_server_name) \
  --restore-time "2024-01-15T13:00:00Z"
```

## Remote State (Recommended for Teams)

Store Terraform state in Azure Storage:

### 1. Create Storage Account for State

```bash
# Variables
RESOURCE_GROUP_NAME="terraform-state-rg"
STORAGE_ACCOUNT_NAME="tfstatepyshop"  # Must be globally unique
CONTAINER_NAME="tfstate"
LOCATION="eastus"

# Create resource group
az group create --name $RESOURCE_GROUP_NAME --location $LOCATION

# Create storage account
az storage account create \
  --resource-group $RESOURCE_GROUP_NAME \
  --name $STORAGE_ACCOUNT_NAME \
  --sku Standard_LRS \
  --encryption-services blob

# Create blob container
az storage container create \
  --name $CONTAINER_NAME \
  --account-name $STORAGE_ACCOUNT_NAME
```

### 2. Configure Backend in main.tf

Uncomment and configure the backend block in `main.tf`:

```hcl
terraform {
  backend "azurerm" {
    resource_group_name  = "terraform-state-rg"
    storage_account_name = "tfstatepyshop"
    container_name       = "tfstate"
    key                  = "pyshop.terraform.tfstate"
  }
}
```

### 3. Initialize with Remote Backend

```bash
terraform init -reconfigure
```

## Cost Optimization

### Development Environment (~$30-50/month)

```hcl
# terraform.tfvars
postgres_sku_name              = "B_Standard_B1ms"    # ~$12/month
postgres_storage_mb            = 32768                # 32GB
postgres_geo_redundant_backup  = false
postgres_high_availability     = false
app_cpu                        = "0.25"
app_memory                     = "0.5Gi"
app_min_replicas               = 1                    # ~$15-20/month
app_max_replicas               = 3
acr_sku                        = "Basic"              # ~$5/month
log_retention_days             = 30
```

### Production Environment (~$150-300/month)

```hcl
# production.tfvars
postgres_sku_name              = "GP_Standard_D2s_v3" # ~$150/month
postgres_storage_mb            = 131072               # 128GB
postgres_geo_redundant_backup  = true
postgres_high_availability     = true                 # Zone-redundant
app_cpu                        = "1.0"
app_memory                     = "2Gi"
app_min_replicas               = 2                    # ~$60-80/month
app_max_replicas               = 20
acr_sku                        = "Standard"           # ~$20/month
log_retention_days             = 90
enable_ddos_protection         = true                 # ~$2900/month
```

**Cost Saving Tips**:
- Use **Burstable (B-series)** database SKUs for dev/test
- Use **Container Apps** instead of App Service (pay-per-use)
- Disable **geo-redundant backups** for non-critical environments
- Reduce **log retention** for development
- Avoid **DDoS Protection Standard** unless required (~$3000/month)
- Use **Basic ACR** tier for small projects

## Troubleshooting

### Container App Not Starting

Check container logs:
```bash
az containerapp logs show \
  --name $(terraform output -raw container_app_name) \
  --resource-group $(terraform output -raw resource_group_name) \
  --tail 100
```

Check revision status:
```bash
az containerapp revision list \
  --name $(terraform output -raw container_app_name) \
  --resource-group $(terraform output -raw resource_group_name) \
  -o table
```

### Database Connection Issues

1. Verify network connectivity from Container App to database
2. Check that database allows connections from the app subnet
3. Verify credentials in Key Vault
4. Test connection:

```bash
# Get into running container
az containerapp exec \
  --name $(terraform output -raw container_app_name) \
  --resource-group $(terraform output -raw resource_group_name) \
  --command "/bin/sh"

# Inside container, test database connection
nc -zv <db-fqdn> 5432
```

### Key Vault Access Denied

Ensure the managed identity has proper access:

```bash
# Grant yourself access to Key Vault
az keyvault set-policy \
  --name $(terraform output -raw key_vault_name) \
  --upn your@email.com \
  --secret-permissions get list set delete
```

## Security Best Practices

1. **Use Managed Identities** - Already configured for Container Apps and App Service
2. **Restrict Network Access** - Update `allowed_ip_ranges` to specific IPs
3. **Enable Private Endpoints** - For production, use private endpoints for ACR and Key Vault
4. **Rotate Secrets** - Regularly rotate database passwords and API keys
5. **Enable Azure Defender** - For threat protection
6. **Use Azure Policy** - Enforce organizational standards
7. **Enable Diagnostic Settings** - For audit logging
8. **Review NSG Rules** - Regularly audit security group rules

## Cleanup

To destroy all infrastructure:

```bash
# Review what will be deleted
terraform plan -destroy

# Destroy infrastructure
terraform destroy
```

**Warning**: This will delete:
- All databases and data
- All containers and images in ACR
- All logs (based on retention settings)
- All secrets in Key Vault (soft-delete enabled, recoverable for 7 days)

## Additional Resources

- [Azure Container Apps Documentation](https://docs.microsoft.com/en-us/azure/container-apps/)
- [Azure Database for PostgreSQL Documentation](https://docs.microsoft.com/en-us/azure/postgresql/)
- [Terraform Azure Provider Documentation](https://registry.terraform.io/providers/hashicorp/azurerm/latest/docs)
- [Azure Pricing Calculator](https://azure.microsoft.com/en-us/pricing/calculator/)

## Support

For issues or questions:
- Azure Support: https://azure.microsoft.com/en-us/support/
- Terraform Azure Provider: https://github.com/hashicorp/terraform-provider-azurerm/issues
- Project Repository: [Add your repo URL]

## License

[Add your license information]
