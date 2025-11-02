# Container Apps Environment
resource "azurerm_container_app_environment" "main" {
  count = var.use_container_apps ? 1 : 0

  name                       = "${var.project_name}-${var.environment}-env"
  location                   = azurerm_resource_group.main.location
  resource_group_name        = azurerm_resource_group.main.name
  log_analytics_workspace_id = azurerm_log_analytics_workspace.main.id
  infrastructure_subnet_id   = azurerm_subnet.app.id

  tags = merge(
    {
      Project     = var.project_name
      Environment = var.environment
      ManagedBy   = "Terraform"
    },
    var.additional_tags
  )
}

# Container App
resource "azurerm_container_app" "main" {
  count = var.use_container_apps ? 1 : 0

  name                         = "${var.project_name}-${var.environment}-app"
  container_app_environment_id = azurerm_container_app_environment.main[0].id
  resource_group_name          = azurerm_resource_group.main.name
  revision_mode                = "Single"

  identity {
    type = "SystemAssigned"
  }

  registry {
    server               = azurerm_container_registry.acr.login_server
    username             = azurerm_container_registry.acr.admin_username
    password_secret_name = "acr-password"
  }

  secret {
    name  = "acr-password"
    value = azurerm_container_registry.acr.admin_password
  }

  secret {
    name  = "secret-key"
    value = var.secret_key != "" ? var.secret_key : random_password.secret_key.result
  }

  secret {
    name  = "database-url"
    value = "postgresql+asyncpg://${var.db_admin_username}:${random_password.postgres.result}@${azurerm_postgresql_flexible_server.main.fqdn}:5432/${var.db_name}"
  }

  template {
    container {
      name   = "pyshop-api"
      image  = var.container_image != "" ? var.container_image : "${azurerm_container_registry.acr.login_server}/pyshop-api:latest"
      cpu    = tonumber(var.app_cpu)
      memory = var.app_memory

      env {
        name  = "DATABASE_URL"
        secret_name = "database-url"
      }

      env {
        name  = "SECRET_KEY"
        secret_name = "secret-key"
      }

      env {
        name  = "ACCESS_TOKEN_EXPIRE_MINUTES"
        value = tostring(var.access_token_expire_minutes)
      }

      env {
        name  = "APPLICATIONINSIGHTS_CONNECTION_STRING"
        value = azurerm_application_insights.main.connection_string
      }

      liveness_probe {
        transport = "HTTP"
        port      = 8000
        path      = "/healthz"
      }

      readiness_probe {
        transport = "HTTP"
        port      = 8000
        path      = "/healthz"
      }
    }

    min_replicas = var.app_min_replicas
    max_replicas = var.app_max_replicas

    http_scale_rule {
      name                = "http-rule"
      concurrent_requests = 100
    }
  }

  ingress {
    external_enabled = true
    target_port      = 8000
    transport        = "auto"

    traffic_weight {
      latest_revision = true
      percentage      = 100
    }
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

# Grant Container App access to Key Vault
resource "azurerm_key_vault_access_policy" "container_app" {
  count = var.use_container_apps ? 1 : 0

  key_vault_id = azurerm_key_vault.main.id
  tenant_id    = data.azurerm_client_config.current.tenant_id
  object_id    = azurerm_container_app.main[0].identity[0].principal_id

  secret_permissions = [
    "Get",
    "List"
  ]
}
