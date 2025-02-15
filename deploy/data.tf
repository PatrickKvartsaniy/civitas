data "aws_caller_identity" "current" {}

data "aws_ecr_authorization_token" "token" {}

# IAM Policy Document for ECR Repository Access
data "aws_iam_policy_document" "default" {
  statement {
    effect = "Allow"

    principals {
      type        = "AWS"
      identifiers = ["*"] # Allow all AWS accounts (modify for security)
    }

    actions = [
      "ecr:BatchGetImage",
      "ecr:GetDownloadUrlForLayer"
    ]
  }
}

## Fetch Latest Amazon ECS Optimized AMI
data "aws_ami" "ecs_optimized" {
  most_recent = true
  owners      = ["amazon"]

  filter {
    name   = "name"
    values = ["amzn2-ami-ecs-hvm-*-x86_64-ebs"]
  }
}
