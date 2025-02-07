## Create ECR repository
resource "aws_ecr_repository" "repository" {
  for_each = toset(var.repository_list)
  name = each.key
}

# Build Docker images
resource "docker_image" "civitas" {
  for_each = toset(var.repository_list)
  name     = "${aws_ecr_repository.repository[each.key].repository_url}:latest"

  build {
    context    = "."
    dockerfile = "${each.key}.Dockerfile"
  }
}

# Push images to ECR
resource "docker_registry_image" "civitas" {
  for_each = toset(var.repository_list)
  name     = docker_image.civitas[each.key].name
}
