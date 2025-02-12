## ECS Cluster
resource "aws_ecs_cluster" "web" {
  name = "civitas-cluster"
}

## Task Definition
variable "docker_images" {
  default = ""
}
resource "aws_ecs_task_definition" "web_task" {
  family       = "web"
  network_mode = "awsvpc"

  lifecycle {
    create_before_destroy = true
  }

  container_definitions = jsonencode([
    {
      name   = "web"
      image  = var.docker_images["web"].name
      cpu    = 256
      memory = 512
      portMappings = [
        {
          containerPort = 8080
          hostPort      = 8080
        }
      ]
    }
  ])
}

## ECS Service
variable "alb_tg_arn" {
  default = ""
}
variable "alb_sg_id" {
  default = ""
}
resource "aws_ecs_service" "web_service" {
  name            = "web"
  cluster         = aws_ecs_cluster.web.id
  task_definition = aws_ecs_task_definition.web_task.arn
  desired_count   = 1
  launch_type     = "EC2"

  network_configuration {
    subnets         = var.subnet_ids
    security_groups = [var.alb_sg_id]
  }

  load_balancer {
    target_group_arn = var.alb_tg_arn
    container_name   = "web"
    container_port   = 8080
  }

  depends_on = [aws_lb_listener.http]
}

output "cluster_name" {
  value = aws_ecs_cluster.web.name
}
