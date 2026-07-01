# ---------------------------------------------------------------------------
# compliance.<domain> - static hosting for the continuous-compliance dashboard.
#
# Mirrors the frontend pattern: a PRIVATE S3 bucket readable only by a dedicated
# CloudFront distribution via Origin Access Control. The distribution is public
# (no auth) - the dashboard is a non-sensitive DEMONSTRATION (no PHI/secrets, and
# the repo is already public) and carries a noindex tag. Reuses the existing
# wildcard ACM cert and hardened response-headers policy.
#
# The specific alias/record (compliance.<domain>) overlaps the main distribution's
# *.<domain> wildcard, which AWS permits, and the specific Route 53 record takes
# precedence over the wildcard for this exact name.
# ---------------------------------------------------------------------------

# ── S3 bucket for the dashboard files ──
resource "aws_s3_bucket" "compliance_dashboard" {
  # checkov:skip=CKV_AWS_18: Dashboard is non-sensitive; access logging not needed.
  # checkov:skip=CKV_AWS_144: Files are regenerable from the repo.
  # checkov:skip=CKV_AWS_145: Public, non-sensitive demo content; SSE-S3 (AES256) is
  #   sufficient. Using the shared s3 CMK would require its OAC decrypt grant to name
  #   this distribution's ARN, creating a distribution->bucket->key->distribution cycle.
  # checkov:skip=CKV2_AWS_61: Bucket re-synced on deploy; no lifecycle needed.
  # checkov:skip=CKV2_AWS_62: No downstream consumer for bucket events.
  bucket        = "aeglero-emr-compliance-dashboard"
  force_destroy = true
}

resource "aws_s3_bucket_versioning" "compliance_dashboard" {
  bucket = aws_s3_bucket.compliance_dashboard.id
  versioning_configuration {
    status = "Enabled"
  }
}

# trivy:ignore:AVD-AWS-0132 -- Public, non-sensitive demo content; SSE-S3 is sufficient. See docs/iac-scan-exceptions.md.
resource "aws_s3_bucket_server_side_encryption_configuration" "compliance_dashboard" {
  bucket = aws_s3_bucket.compliance_dashboard.id
  rule {
    apply_server_side_encryption_by_default {
      sse_algorithm = "AES256" # SSE-S3: public, non-sensitive content; keeps OAC simple.
    }
  }
}

resource "aws_s3_bucket_public_access_block" "compliance_dashboard" {
  bucket                  = aws_s3_bucket.compliance_dashboard.id
  block_public_acls       = true
  block_public_policy     = true
  ignore_public_acls      = true
  restrict_public_buckets = true
}

# Only the compliance distribution may read the bucket.
resource "aws_s3_bucket_policy" "compliance_dashboard" {
  bucket = aws_s3_bucket.compliance_dashboard.id
  policy = jsonencode({
    Version = "2012-10-17"
    Statement = [{
      Sid       = "AllowCloudFrontServicePrincipalReadOnly"
      Effect    = "Allow"
      Principal = { Service = "cloudfront.amazonaws.com" }
      Action    = "s3:GetObject"
      Resource  = "${aws_s3_bucket.compliance_dashboard.arn}/*"
      Condition = {
        StringEquals = {
          "AWS:SourceArn" = aws_cloudfront_distribution.compliance_dashboard.arn
        }
      }
    }]
  })
}

# ── Upload the dashboard files. etag=filemd5 re-uploads them when they change on
#    a subsequent apply. (A CI `aws s3 sync` step can keep data.js fresher.) ──
resource "aws_s3_object" "compliance_index" {
  bucket       = aws_s3_bucket.compliance_dashboard.id
  key          = "index.html"
  source       = "${path.module}/../compliance/dashboard/index.html"
  etag         = filemd5("${path.module}/../compliance/dashboard/index.html")
  content_type = "text/html"
}

resource "aws_s3_object" "compliance_data" {
  bucket       = aws_s3_bucket.compliance_dashboard.id
  key          = "data.js"
  source       = "${path.module}/../compliance/dashboard/data.js"
  etag         = filemd5("${path.module}/../compliance/dashboard/data.js")
  content_type = "application/javascript"
}

resource "aws_s3_object" "compliance_logo" {
  bucket       = aws_s3_bucket.compliance_dashboard.id
  key          = "logo.png"
  source       = "${path.module}/../compliance/dashboard/logo.png"
  etag         = filemd5("${path.module}/../compliance/dashboard/logo.png")
  content_type = "image/png"
}

# The AI Review tab's data feed (window.AI_REVIEW). Committed snapshot; the
# dashboard-deploy workflow re-syncs a fresher copy on each weekly run.
resource "aws_s3_object" "compliance_ai_review" {
  bucket       = aws_s3_bucket.compliance_dashboard.id
  key          = "ai_review.js"
  source       = "${path.module}/../compliance/dashboard/ai_review.js"
  etag         = filemd5("${path.module}/../compliance/dashboard/ai_review.js")
  content_type = "application/javascript"
}

# ── Origin Access Control ──
resource "aws_cloudfront_origin_access_control" "compliance_dashboard" {
  name                              = "aeglero-compliance-dashboard"
  origin_access_control_origin_type = "s3"
  signing_behavior                  = "always"
  signing_protocol                  = "sigv4"
}

# ── CloudFront distribution ──
resource "aws_cloudfront_distribution" "compliance_dashboard" {
  # checkov:skip=CKV_AWS_310: Single-origin static site; no origin failover needed.
  # checkov:skip=CKV_AWS_374: Geo restriction not in use (public demo).
  # checkov:skip=CKV2_AWS_47: Static site; WAF Log4j rule not applicable.
  enabled             = true
  is_ipv6_enabled     = true
  comment             = "Aeglero - continuous compliance dashboard"
  default_root_object = "index.html"
  price_class         = "PriceClass_100"

  aliases = ["compliance.${var.domain_name}"]

  web_acl_id = var.enable_waf ? aws_wafv2_web_acl.cloudfront[0].arn : null

  dynamic "logging_config" {
    for_each = var.enable_cloudfront_access_logs ? [1] : []
    content {
      bucket          = aws_s3_bucket.access_logs[0].bucket_domain_name
      include_cookies = false
      prefix          = "compliance/"
    }
  }

  origin {
    domain_name              = aws_s3_bucket.compliance_dashboard.bucket_regional_domain_name
    origin_id                = "s3-compliance"
    origin_access_control_id = aws_cloudfront_origin_access_control.compliance_dashboard.id
  }

  default_cache_behavior {
    allowed_methods        = ["GET", "HEAD", "OPTIONS"]
    cached_methods         = ["GET", "HEAD"]
    target_origin_id       = "s3-compliance"
    viewer_protocol_policy = "redirect-to-https"
    compress               = true

    # CachingOptimized (AWS managed) - edge-cache the static assets so repeated or
    # abusive requests are absorbed at the CloudFront edge instead of hitting S3,
    # bounding origin load and cost. The dashboard-deploy workflow runs a CloudFront
    # invalidation on every publish, so new content still appears immediately.
    cache_policy_id            = "658327ea-f89d-4fab-a63d-7e88639e58f6"
    response_headers_policy_id = aws_cloudfront_response_headers_policy.security.id
  }

  restrictions {
    geo_restriction {
      restriction_type = "none"
    }
  }

  viewer_certificate {
    acm_certificate_arn      = aws_acm_certificate_validation.cloudfront.certificate_arn
    ssl_support_method       = "sni-only"
    minimum_protocol_version = "TLSv1.2_2021"
  }
}

# ── DNS: compliance.<domain> -> the dashboard distribution ──
resource "aws_route53_record" "compliance_dashboard" {
  zone_id = var.hosted_zone_id
  name    = "compliance.${var.domain_name}"
  type    = "A"
  alias {
    name                   = aws_cloudfront_distribution.compliance_dashboard.domain_name
    zone_id                = aws_cloudfront_distribution.compliance_dashboard.hosted_zone_id
    evaluate_target_health = false
  }
}

resource "aws_route53_record" "compliance_dashboard_ipv6" {
  zone_id = var.hosted_zone_id
  name    = "compliance.${var.domain_name}"
  type    = "AAAA"
  alias {
    name                   = aws_cloudfront_distribution.compliance_dashboard.domain_name
    zone_id                = aws_cloudfront_distribution.compliance_dashboard.hosted_zone_id
    evaluate_target_health = false
  }
}

output "compliance_dashboard_url" {
  description = "Public URL of the continuous-compliance dashboard"
  value       = "https://compliance.${var.domain_name}"
}
