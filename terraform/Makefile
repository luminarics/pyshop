.PHONY: help init plan apply destroy validate fmt clean lint check

# Default target
help:
	@echo "Available targets:"
	@echo "  init      - Initialize Terraform"
	@echo "  validate  - Validate Terraform configuration"
	@echo "  fmt       - Format Terraform files"
	@echo "  plan      - Show execution plan"
	@echo "  apply     - Apply Terraform changes"
	@echo "  destroy   - Destroy Terraform-managed infrastructure"
	@echo "  clean     - Remove Terraform cache and state backups"
	@echo "  lint      - Run tflint (requires tflint installed)"
	@echo "  check     - Run validate + fmt + lint"
	@echo ""
	@echo "Environment-specific targets:"
	@echo "  plan-dev       - Plan for dev environment"
	@echo "  apply-dev      - Apply for dev environment"
	@echo "  plan-staging   - Plan for staging environment"
	@echo "  apply-staging  - Apply for staging environment"
	@echo "  plan-prod      - Plan for production environment"
	@echo "  apply-prod     - Apply for production environment"

# Initialize Terraform
init:
	terraform init

# Validate configuration
validate:
	terraform validate

# Format Terraform files
fmt:
	terraform fmt -recursive

# Show execution plan
plan:
	terraform plan

# Apply changes
apply:
	terraform apply

# Destroy infrastructure
destroy:
	@echo "WARNING: This will destroy all infrastructure!"
	@echo "Press Ctrl+C to cancel, or wait 10 seconds to continue..."
	@sleep 10
	terraform destroy

# Clean up
clean:
	rm -rf .terraform
	rm -f .terraform.lock.hcl
	find . -name "*.tfstate.backup" -delete

# Lint (requires tflint)
lint:
	@which tflint > /dev/null || (echo "tflint not installed. Install from https://github.com/terraform-linters/tflint" && exit 1)
	tflint --init
	tflint

# Run all checks
check: validate fmt lint
	@echo "All checks passed!"

# Environment-specific targets
plan-dev:
	terraform workspace select dev || terraform workspace new dev
	terraform plan -var-file="dev.tfvars"

apply-dev:
	terraform workspace select dev || terraform workspace new dev
	terraform apply -var-file="dev.tfvars"

plan-staging:
	terraform workspace select staging || terraform workspace new staging
	terraform plan -var-file="staging.tfvars"

apply-staging:
	terraform workspace select staging || terraform workspace new staging
	terraform apply -var-file="staging.tfvars"

plan-prod:
	terraform workspace select production || terraform workspace new production
	terraform plan -var-file="production.tfvars"

apply-prod:
	terraform workspace select production || terraform workspace new production
	terraform apply -var-file="production.tfvars"

# Get outputs
output:
	terraform output

# Show current state
show:
	terraform show

# Refresh state
refresh:
	terraform refresh

# Import existing resource (usage: make import RESOURCE=aws_instance.example ID=i-1234567890abcdef0)
import:
	terraform import $(RESOURCE) $(ID)

# Taint resource (usage: make taint RESOURCE=aws_instance.example)
taint:
	terraform taint $(RESOURCE)

# Untaint resource (usage: make untaint RESOURCE=aws_instance.example)
untaint:
	terraform untaint $(RESOURCE)
