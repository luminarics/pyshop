variable "project_name" {
  description = "Project name used for resource naming"
  type        = string
  default     = "pyshop"
}

variable "environment" {
  description = "Environment name (dev, staging, production)"
  type        = string
  default     = "dev"
}

variable "location" {
  description = "Azure region for resources"
  type        = string
  default     = "eastus"
}

# Networking
variable "vnet_address_space" {
  description = "Address space for the virtual network"
  type        = list(string)
  default     = ["10.0.0.0/16"]
}

variable "subnet_address_prefix" {
  description = "Address prefix for the app subnet"
  type        = string
  default     = "10.0.1.0/24"
}

variable "db_subnet_address_prefix" {
  description = "Address prefix for the database subnet"
  type        = string
  default     = "10.0.2.0/24"
}

# Database
variable "postgres_version" {
  description = "PostgreSQL version"
  type        = string
  default     = "16"
}

variable "postgres_sku_name" {
  description = "PostgreSQL SKU name (B_Standard_B1ms for dev, GP_Standard_D2s_v3 for production)"
  type        = string
  default     = "B_Standard_B1ms"
}

variable "postgres_storage_mb" {
  description = "PostgreSQL storage in MB"
  type        = number
  default     = 32768
}

variable "postgres_backup_retention_days" {
  description = "Backup retention period in days"
  type        = number
  default     = 7
}

variable "postgres_geo_redundant_backup" {
  description = "Enable geo-redundant backups"
  type        = bool
  default     = false
}

variable "postgres_high_availability" {
  description = "Enable high availability (zone-redundant)"
  type        = bool
  default     = false
}

variable "db_name" {
  description = "Database name"
  type        = string
  default     = "fastapi"
}

variable "db_admin_username" {
  description = "Database administrator username"
  type        = string
  default     = "psqladmin"
}

# App Service / Container Apps
variable "use_container_apps" {
  description = "Use Azure Container Apps instead of App Service (recommended for containerized apps)"
  type        = bool
  default     = true
}

variable "app_cpu" {
  description = "CPU allocation for container (0.25, 0.5, 0.75, 1.0, 1.25, 1.5, 1.75, 2.0)"
  type        = string
  default     = "0.5"
}

variable "app_memory" {
  description = "Memory allocation for container (0.5Gi, 1Gi, 1.5Gi, 2Gi, 3Gi, 3.5Gi, 4Gi)"
  type        = string
  default     = "1Gi"
}

variable "app_min_replicas" {
  description = "Minimum number of container replicas"
  type        = number
  default     = 1
}

variable "app_max_replicas" {
  description = "Maximum number of container replicas"
  type        = number
  default     = 10
}

variable "container_image" {
  description = "Container image to deploy (e.g., <registry>.azurecr.io/pyshop-api:latest)"
  type        = string
  default     = ""
}

# Container Registry
variable "acr_sku" {
  description = "Azure Container Registry SKU (Basic, Standard, Premium)"
  type        = string
  default     = "Basic"
}

# Monitoring
variable "log_retention_days" {
  description = "Log retention period in days"
  type        = number
  default     = 30
}

# Security
variable "allowed_ip_ranges" {
  description = "List of IP ranges allowed to access the application"
  type        = list(string)
  default     = ["0.0.0.0/0"]
}

variable "enable_ddos_protection" {
  description = "Enable DDoS Protection Standard (expensive, recommended for production only)"
  type        = bool
  default     = false
}

# Application Configuration
variable "secret_key" {
  description = "Secret key for JWT signing (will be stored in Key Vault)"
  type        = string
  sensitive   = true
  default     = ""
}

variable "access_token_expire_minutes" {
  description = "JWT access token expiration time in minutes"
  type        = number
  default     = 30
}

# Tags
variable "additional_tags" {
  description = "Additional tags to apply to all resources"
  type        = map(string)
  default     = {}
}
