## Create ECR Repositories
resource "aws_ecr_repository" "repository" {
  for_each = toset(var.repository_list)
  name     = each.key
}

## Build and Push Docker Images
resource "docker_image" "civitas" {
  for_each = toset(var.repository_list)
  name     = "${aws_ecr_repository.repository[each.key].repository_url}:latest"

  build {
    context    = "."
    dockerfile = "${each.key}.Dockerfile"
  }
}

resource "docker_registry_image" "civitas" {
  for_each = toset(var.repository_list)
  name     = docker_image.civitas[each.key].name
}

## ECR Repository Policy
resource "aws_ecr_repository_policy" "default" {
  for_each   = aws_ecr_repository.repository
  repository = each.value.name
  policy     = data.aws_iam_policy_document.default.json
}

output "docker_images" {
  value = docker_registry_image.civitas
}
