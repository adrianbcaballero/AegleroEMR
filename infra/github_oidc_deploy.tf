# ---------------------------------------------------------------------------
# GitHub OIDC -> write-scoped IAM role for publishing the compliance dashboard.
#
# Lets the "Deploy Compliance Dashboard" workflow assume a role at runtime (NO
# stored AWS secrets) that can ONLY sync the dashboard bucket and invalidate the
# compliance CloudFront distribution. It is deliberately separate from the
# read-only live-checks role (github_oidc.tf): that one can Describe cloud
# resources but not write; this one can write the dashboard but not read data.
#
# Trust is scoped to this repo's main branch, since deploys should only ever run
# from main (scheduled runs and manual dispatches both use the default branch).
#
# Apply with `terraform apply`, then set the role ARN as the GitHub repo variable
# AWS_COMPLIANCE_DEPLOY_ROLE_ARN and the distribution id as COMPLIANCE_DISTRIBUTION_ID.
# ---------------------------------------------------------------------------

resource "aws_iam_role" "compliance_deploy" {
  name        = "aeglero-compliance-deploy"
  description = "Write-scoped role assumed by the dashboard-deploy workflow via GitHub OIDC"

  assume_role_policy = jsonencode({
    Version = "2012-10-17"
    Statement = [{
      Effect    = "Allow"
      Principal = { Federated = aws_iam_openid_connect_provider.github.arn }
      Action    = "sts:AssumeRoleWithWebIdentity"
      Condition = {
        StringEquals = {
          "token.actions.githubusercontent.com:aud" = "sts.amazonaws.com"
          # Deploys run only from main; tighter than the read-only role's repo-wide scope.
          "token.actions.githubusercontent.com:sub" = "repo:${var.github_repo}:ref:refs/heads/main"
        }
      }
    }]
  })

  tags = {
    Name    = "aeglero-compliance-deploy"
    Project = "aeglero-emr"
  }
}

# Least-privilege: publish the dashboard objects and bust the CDN cache. Nothing
# else. All actions here support resource-level scoping, so each is pinned to the
# specific bucket / distribution (no Resource="*").
resource "aws_iam_role_policy" "compliance_deploy" {
  name = "compliance-dashboard-publish"
  role = aws_iam_role.compliance_deploy.id

  policy = jsonencode({
    Version = "2012-10-17"
    Statement = [
      {
        Sid      = "ListDashboardBucket"
        Effect   = "Allow"
        Action   = ["s3:ListBucket"]
        Resource = aws_s3_bucket.compliance_dashboard.arn
      },
      {
        Sid      = "WriteDashboardObjects"
        Effect   = "Allow"
        Action   = ["s3:PutObject", "s3:DeleteObject"]
        Resource = "${aws_s3_bucket.compliance_dashboard.arn}/*"
      },
      {
        Sid      = "InvalidateDashboardCdn"
        Effect   = "Allow"
        Action   = ["cloudfront:CreateInvalidation", "cloudfront:GetInvalidation"]
        Resource = aws_cloudfront_distribution.compliance_dashboard.arn
      },
    ]
  })
}

output "compliance_deploy_role_arn" {
  description = "Set this as the GitHub repo variable AWS_COMPLIANCE_DEPLOY_ROLE_ARN"
  value       = aws_iam_role.compliance_deploy.arn
}

output "compliance_distribution_id" {
  description = "Set this as the GitHub repo variable COMPLIANCE_DISTRIBUTION_ID"
  value       = aws_cloudfront_distribution.compliance_dashboard.id
}
