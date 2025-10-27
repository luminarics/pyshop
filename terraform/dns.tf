# Data source for existing Route53 zone (if you have one)
# Uncomment and modify if you're using an existing hosted zone
# data "aws_route53_zone" "main" {
#   name         = var.domain_name
#   private_zone = false
# }

# Create a new hosted zone (comment this out if using existing zone)
resource "aws_route53_zone" "main" {
  count = var.enable_ssl && var.create_route53_zone ? 1 : 0
  name  = var.domain_name

  tags = {
    Name = "${var.project_name}-${var.environment}-zone"
  }
}

# ACM Certificate
resource "aws_acm_certificate" "main" {
  count             = var.enable_ssl ? 1 : 0
  domain_name       = var.domain_name
  validation_method = "DNS"

  subject_alternative_names = [
    "*.${var.domain_name}"
  ]

  tags = {
    Name = "${var.project_name}-${var.environment}-cert"
  }

  lifecycle {
    create_before_destroy = true
  }
}

# Route53 record for ACM certificate validation
resource "aws_route53_record" "cert_validation" {
  for_each = var.enable_ssl ? {
    for dvo in aws_acm_certificate.main[0].domain_validation_options : dvo.domain_name => {
      name   = dvo.resource_record_name
      record = dvo.resource_record_value
      type   = dvo.resource_record_type
    }
  } : {}

  allow_overwrite = true
  name            = each.value.name
  records         = [each.value.record]
  ttl             = 60
  type            = each.value.type
  zone_id         = var.create_route53_zone ? aws_route53_zone.main[0].zone_id : var.route53_zone_id
}

# ACM Certificate Validation
resource "aws_acm_certificate_validation" "main" {
  count                   = var.enable_ssl ? 1 : 0
  certificate_arn         = aws_acm_certificate.main[0].arn
  validation_record_fqdns = [for record in aws_route53_record.cert_validation : record.fqdn]
}

# Route53 A Record pointing to ALB
resource "aws_route53_record" "app" {
  count   = var.enable_ssl ? 1 : 0
  zone_id = var.create_route53_zone ? aws_route53_zone.main[0].zone_id : var.route53_zone_id
  name    = var.domain_name
  type    = "A"

  alias {
    name                   = aws_lb.main.dns_name
    zone_id                = aws_lb.main.zone_id
    evaluate_target_health = true
  }
}

# Route53 A Record for www subdomain
resource "aws_route53_record" "www" {
  count   = var.enable_ssl ? 1 : 0
  zone_id = var.create_route53_zone ? aws_route53_zone.main[0].zone_id : var.route53_zone_id
  name    = "www.${var.domain_name}"
  type    = "A"

  alias {
    name                   = aws_lb.main.dns_name
    zone_id                = aws_lb.main.zone_id
    evaluate_target_health = true
  }
}
