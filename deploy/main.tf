## Create ECR repository
resource "aws_ecr_repository" "repository" {
  for_each = toset(var.repository_list)
  name     = each.key
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

# Apply repository policy for all repositories
resource "aws_ecr_repository_policy" "default" {
  for_each   = aws_ecr_repository.repository
  repository = each.value.name
  policy     = data.aws_iam_policy_document.default.json
}

## Create ECS Cluster
resource "aws_ecs_cluster" "main" {
  name = "civitas-cluster"
}

## Create IAM Role for ECS EC2 Instances
resource "aws_iam_role" "ecs_instance_role" {
  name = "ecsInstanceRole"
  assume_role_policy = jsonencode({
    Statement = [{
      Effect = "Allow"
      Principal = { Service = "ec2.amazonaws.com" }
      Action = "sts:AssumeRole"
    }]
  })
}

# Attach necessary ECS policies to EC2 instance IAM role
resource "aws_iam_role_policy_attachment" "ecs_policy" {
  role       = aws_iam_role.ecs_instance_role.name
  policy_arn = "arn:aws:iam::aws:policy/service-role/AmazonEC2ContainerServiceforEC2Role"
}

## Create ECS Task Definitions (One for Each Service)
resource "aws_ecs_task_definition" "civitas" {
  for_each = toset(var.repository_list)
  family   = each.key # Use service name as family

  container_definitions = jsonencode([
    {
      name  = each.key
      image = docker_registry_image.civitas[each.key].name
      portMappings = [
        {
          containerPort = each.key == "web" ? 5000 : 8080 # Web on port 5000, others 8080
          hostPort      = each.key == "web" ? 80 : 8080  # Map web to 80, others to 8080
        }
      ]
      cpu    = 256 # Adjust as needed
      memory = 512 # Adjust as needed
    }
  ])
}

## Create ECS Service (One for Each Service)
resource "aws_ecs_service" "civitas" {
  for_each = toset(var.repository_list)
  name                  = each.key
  cluster               = aws_ecs_cluster.main.id
  task_definition       = aws_ecs_task_definition.civitas[each.key].arn
  desired_count         = 1 # Adjust as needed
  launch_type           = "EC2"

  depends_on = [aws_ecs_task_definition.civitas]
}

# Output Public IP (for Web Service)
output "web_service_url" {
  value = "ECS is running. Use Load Balancer or EC2 instance IP."
}
