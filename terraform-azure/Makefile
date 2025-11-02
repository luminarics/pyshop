.PHONY: help init plan apply destroy clean validate format lint

# Variables
ENV ?= dev
TFVARS_FILE = $(ENV).tfvars

help: ## Show this help message
	@echo 'Usage: make [target] [ENV=environment]'
	@echo ''
	@echo 'Available targets:'
	@awk 'BEGIN {FS = ":.*?## "} /^[a-zA-Z_-]+:.*?## / {printf "  %-20s %s\n", $$1, $$2}' $(MAKEFILE_LIST)
	@echo ''
	@echo 'Available environments: dev, staging, production'
	@echo 'Example: make plan ENV=production'

init: ## Initialize Terraform
	terraform init

validate: ## Validate Terraform configuration
	terraform validate

format: ## Format Terraform files
	terraform fmt -recursive

lint: validate format ## Lint and format Terraform files
	@echo "Linting complete"

plan: ## Create Terraform execution plan
	@if [ -f $(TFVARS_FILE) ]; then \
		terraform plan -var-file=$(TFVARS_FILE); \
	else \
		terraform plan; \
	fi

apply: ## Apply Terraform changes
	@if [ -f $(TFVARS_FILE) ]; then \
		terraform apply -var-file=$(TFVARS_FILE); \
	else \
		terraform apply; \
	fi

destroy: ## Destroy Terraform-managed infrastructure
	@if [ -f $(TFVARS_FILE) ]; then \
		terraform destroy -var-file=$(TFVARS_FILE); \
	else \
		terraform destroy; \
	fi

clean: ## Clean Terraform files
	rm -rf .terraform
	rm -f .terraform.lock.hcl
	rm -f terraform.tfstate
	rm -f terraform.tfstate.backup
	rm -f *.tfplan

output: ## Show Terraform outputs
	terraform output

refresh: ## Refresh Terraform state
	terraform refresh

show: ## Show Terraform state
	terraform show

# Azure-specific commands
login: ## Login to Azure CLI
	az login

acr-login: ## Login to Azure Container Registry
	@ACR_NAME=$$(terraform output -raw container_registry_name 2>/dev/null); \
	if [ -n "$$ACR_NAME" ]; then \
		az acr login --name $$ACR_NAME; \
	else \
		echo "Error: Could not get ACR name. Run 'terraform apply' first."; \
	fi

push-image: acr-login ## Build and push Docker image to ACR
	@cd .. && docker build -t pyshop-api:latest .
	@ACR_SERVER=$$(terraform output -raw container_registry_login_server); \
	docker tag pyshop-api:latest $$ACR_SERVER/pyshop-api:latest; \
	docker push $$ACR_SERVER/pyshop-api:latest

update-app: ## Update Container App with new image
	@APP_NAME=$$(terraform output -raw container_app_name 2>/dev/null); \
	RG_NAME=$$(terraform output -raw resource_group_name 2>/dev/null); \
	ACR_SERVER=$$(terraform output -raw container_registry_login_server 2>/dev/null); \
	if [ -n "$$APP_NAME" ] && [ -n "$$RG_NAME" ] && [ -n "$$ACR_SERVER" ]; then \
		az containerapp update \
			--name $$APP_NAME \
			--resource-group $$RG_NAME \
			--image $$ACR_SERVER/pyshop-api:latest; \
	else \
		echo "Error: Could not get app details. Run 'terraform apply' first."; \
	fi

logs: ## Show Container App logs
	@APP_NAME=$$(terraform output -raw container_app_name 2>/dev/null); \
	RG_NAME=$$(terraform output -raw resource_group_name 2>/dev/null); \
	if [ -n "$$APP_NAME" ] && [ -n "$$RG_NAME" ]; then \
		az containerapp logs show \
			--name $$APP_NAME \
			--resource-group $$RG_NAME \
			--follow; \
	else \
		echo "Error: Could not get app details. Run 'terraform apply' first."; \
	fi

db-migrate: ## Run database migrations
	@echo "Running database migrations..."
	@APP_NAME=$$(terraform output -raw container_app_name 2>/dev/null); \
	RG_NAME=$$(terraform output -raw resource_group_name 2>/dev/null); \
	if [ -n "$$APP_NAME" ] && [ -n "$$RG_NAME" ]; then \
		az containerapp exec \
			--name $$APP_NAME \
			--resource-group $$RG_NAME \
			--command "alembic upgrade head"; \
	else \
		echo "Error: Could not get app details. Run 'terraform apply' first."; \
	fi

cost-estimate: ## Show estimated monthly costs
	@echo "Estimated monthly costs for $(ENV) environment:"
	@echo "This requires Azure Cost Management API or manual calculation"
	@echo "Visit: https://azure.microsoft.com/en-us/pricing/calculator/"
