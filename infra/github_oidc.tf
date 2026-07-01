# ---------------------------------------------------------------------------
# GitHub OIDC -> read-only IAM role for the continuous-compliance live checks.
#
# Lets the "Continuous Compliance (Live AWS)" GitHub Actions workflow assume a
# READ-ONLY role at runtime with NO stored AWS secrets. The trust policy is
# scoped to this repository only. Apply with `terraform apply`, then set the
# role ARN as a GitHub repo variable named AWS_COMPLIANCE_ROLE_ARN.
# ---------------------------------------------------------------------------

variable "github_repo" {
  description = "owner/repo permitted to assume the compliance read-only role"
  type        = string
  default     = "adrianbcaballero/AegleroEMR"
}

# GitHub's OIDC identity provider. If your account already has one for
# token.actions.githubusercontent.com, delete this resource and reference the
# existing provider's ARN in the role trust policy below instead.
resource "aws_iam_openid_connect_provider" "github" {
  url            = "https://token.actions.githubusercontent.com"
  client_id_list = ["sts.amazonaws.com"]
  thumbprint_list = [
    "6938fd4d98bab03faadb97b34396831e3780aea1",
    "1c58a3a8518e8759bf075b76b750d4f2df264fcd",
  ]

  tags = {
    Name    = "github-actions-oidc"
    Project = "aeglero-emr"
  }
}

resource "aws_iam_role" "compliance_readonly" {
  name        = "aeglero-compliance-readonly"
  description = "Read-only role assumed by the compliance live-verification workflow via GitHub OIDC"

  assume_role_policy = jsonencode({
    Version = "2012-10-17"
    Statement = [{
      Effect    = "Allow"
      Principal = { Federated = aws_iam_openid_connect_provider.github.arn }
      Action    = "sts:AssumeRoleWithWebIdentity"
      Condition = {
        StringEquals = {
          "token.actions.githubusercontent.com:aud" = "sts.amazonaws.com"
        }
        # Restrict to this repository (any branch/workflow). Tighten to a ref,
        # e.g. repo:owner/name:ref:refs/heads/main, if you want branch scoping.
        StringLike = {
          "token.actions.githubusercontent.com:sub" = "repo:${var.github_repo}:*"
        }
      }
    }]
  })

  tags = {
    Name    = "aeglero-compliance-readonly"
    Project = "aeglero-emr"
  }
}

# Least-privilege: only the read APIs the live collectors call. No write actions,
# no secret access, no data-plane reads.
resource "aws_iam_role_policy" "compliance_readonly" {
  # checkov:skip=CKV_AWS_355: The kms/rds/elb Describe and List actions used here
  # do not support resource-level permissions - AWS requires Resource="*" for them.
  # The policy is still least-privilege: read-only, no write/secret/data-plane access.
  name = "compliance-readonly-describe"
  role = aws_iam_role.compliance_readonly.id

  policy = jsonencode({
    Version = "2012-10-17"
    Statement = [{
      Effect = "Allow"
      Action = [
        "sts:GetCallerIdentity",
        "kms:ListKeys",
        "kms:DescribeKey",
        "kms:GetKeyRotationStatus",
        "rds:DescribeDBInstances",
        "rds:DescribeDBParameters",
        "rds:DescribeDBParameterGroups",
        "elasticloadbalancing:DescribeLoadBalancers",
        "elasticloadbalancing:DescribeListeners",
      ]
      Resource = "*"
    }]
  })
}

output "compliance_role_arn" {
  description = "Set this as the GitHub repo variable AWS_COMPLIANCE_ROLE_ARN"
  value       = aws_iam_role.compliance_readonly.arn
}
