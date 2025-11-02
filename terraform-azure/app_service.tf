# App Service Plan (Alternative to Container Apps)
resource "azurerm_service_plan" "main" {
  count = var.use_container_apps ? 0 : 1

  name                = "${var.project_name}-${var.environment}-plan"
  location            = azurerm_resource_group.main.location
  resource_group_name = azurerm_resource_group.main.name
  os_type             = "Linux"
  sku_name            = "B1" # Basic tier, change to P1v2 or higher for production

  tags = merge(
    {
      Project     = var.project_name
      Environment = var.environment
      ManagedBy   = "Terraform"
    },
    var.additional_tags
  )
}

# Linux Web App (App Service)
resource "azurerm_linux_web_app" "main" {
  count = var.use_container_apps ? 0 : 1

  name                = "${var.project_name}-${var.environment}-app-${random_string.unique.result}"
  location            = azurerm_resource_group.main.location
  resource_group_name = azurerm_resource_group.main.name
  service_plan_id     = azurerm_service_plan.main[0].id

  identity {
    type = "SystemAssigned"
  }

  site_config {
    always_on = true

    application_stack {
      docker_image_name   = var.container_image != "" ? var.container_image : "pyshop-api:latest"
      docker_registry_url = "https://${azurerm_container_registry.acr.login_server}"
      docker_registry_username = azurerm_container_registry.acr.admin_username
      docker_registry_password = azurerm_container_registry.acr.admin_password
    }

    health_check_path = "/healthz"
  }

  app_settings = {
    "WEBSITES_ENABLE_APP_SERVICE_STORAGE" = "false"
    "DOCKER_REGISTRY_SERVER_URL"          = "https://${azurerm_container_registry.acr.login_server}"
    "DOCKER_REGISTRY_SERVER_USERNAME"     = azurerm_container_registry.acr.admin_username
    "DOCKER_REGISTRY_SERVER_PASSWORD"     = azurerm_container_registry.acr.admin_password
    "WEBSITES_PORT"                       = "8000"
    "DATABASE_URL"                        = "@Microsoft.KeyVault(SecretUri=${azurerm_key_vault_secret.db_connection_string.versionless_id})"
    "SECRET_KEY"                          = "@Microsoft.KeyVault(SecretUri=${azurerm_key_vault_secret.app_secret_key.versionless_id})"
    "ACCESS_TOKEN_EXPIRE_MINUTES"         = tostring(var.access_token_expire_minutes)
    "APPLICATIONINSIGHTS_CONNECTION_STRING" = azurerm_application_insights.main.connection_string
  }

  tags = merge(
    {
      Project     = var.project_name
      Environment = var.environment
      ManagedBy   = "Terraform"
    },
    var.additional_tags
  )

  depends_on = [
    azurerm_postgresql_flexible_server.main,
    azurerm_postgresql_flexible_server_database.main
  ]
}

# Grant App Service access to Key Vault
resource "azurerm_key_vault_access_policy" "app_service" {
  count = var.use_container_apps ? 0 : 1

  key_vault_id = azurerm_key_vault.main.id
  tenant_id    = data.azurerm_client_config.current.tenant_id
  object_id    = azurerm_linux_web_app.main[0].identity[0].principal_id

  secret_permissions = [
    "Get",
    "List"
  ]
}
