## Create ECR Repository
resource "aws_ecr_repository" "repository" {
  for_each = toset(var.repository_list)
  name     = each.key
}

# Build Docker Images
resource "docker_image" "civitas" {
  for_each = toset(var.repository_list)
  name     = "${aws_ecr_repository.repository[each.key].repository_url}:latest"

  build {
    context    = "."
    dockerfile = "${each.key}.Dockerfile"
  }
}

# Push Images to ECR
resource "docker_registry_image" "civitas" {
  for_each = toset(var.repository_list)
  name     = docker_image.civitas[each.key].name
}

# Apply Repository Policy for All Repositories
resource "aws_ecr_repository_policy" "default" {
  for_each   = aws_ecr_repository.repository
  repository = each.value.name
  policy     = data.aws_iam_policy_document.default.json
}

## Create ECS Cluster (for "web" only)
resource "aws_ecs_cluster" "web" {
  name = "civitas-cluster"
}

## Create IAM Role for ECS EC2 Instances
resource "aws_iam_role" "ecs_instance_role" {
  name = "ecsInstanceRole"
  assume_role_policy = jsonencode({
    Statement = [{
      Effect    = "Allow"
      Principal = { Service = "ec2.amazonaws.com" }
      Action    = "sts:AssumeRole"
    }]
  })
}

# Attach Necessary ECS Policies to EC2 Instance IAM Role
resource "aws_iam_role_policy_attachment" "ecs_policy" {
  role       = aws_iam_role.ecs_instance_role.name
  policy_arn = "arn:aws:iam::aws:policy/service-role/AmazonEC2ContainerServiceforEC2Role"
}

## Create Security Group for ALB
resource "aws_security_group" "alb_sg" {
  name        = "alb-security-group"
  description = "Allow inbound HTTP traffic"

  ingress {
    from_port   = 80
    to_port     = 80
    protocol    = "tcp"
    cidr_blocks = ["0.0.0.0/0"]
  }

  egress {
    from_port   = 0
    to_port     = 0
    protocol    = "-1"
    cidr_blocks = ["0.0.0.0/0"]
  }
}

## Create Load Balancer
resource "aws_lb" "civitas_alb" {
  name               = "civitas-alb"
  internal           = false
  load_balancer_type = "application"
  security_groups    = [aws_security_group.alb_sg.id]
  subnets            = var.subnet_ids
}

## Create Target Group for ALB
resource "aws_lb_target_group" "civitas_tg" {
  name        = "civitas-target-group"
  port        = 80
  protocol    = "HTTP"
  vpc_id      = var.vpc_id
  target_type = "ip"

  health_check {
    path                = "/"
    interval            = 30
    timeout             = 5
    healthy_threshold   = 3
    unhealthy_threshold = 3
  }
}

## Create ALB Listener
resource "aws_lb_listener" "http" {
  load_balancer_arn = aws_lb.civitas_alb.arn
  port              = 80
  protocol          = "HTTP"

  default_action {
    type             = "forward"
    target_group_arn = aws_lb_target_group.civitas_tg.arn
  }
}

## Create ECS Task Definition (Only for "web")
resource "aws_ecs_task_definition" "web_task" {
  family       = "web"
  network_mode = "awsvpc"

  lifecycle {
    create_before_destroy = true
  }

  container_definitions = jsonencode([
    {
      name   = "web"
      image  = docker_registry_image.civitas["web"].name
      cpu    = 256
      memory = 512
      portMappings = [
        {
          containerPort = 8080
          hostPort      = 8080
        }
    ] }
  ])
}

## Create ECS Service (Only for "web")
resource "aws_ecs_service" "web_service" {
  name            = "web"
  cluster         = aws_ecs_cluster.web.id
  task_definition = aws_ecs_task_definition.web_task.arn
  desired_count   = 1
  launch_type     = "EC2"

  network_configuration {
    subnets         = var.subnet_ids
    security_groups = [aws_security_group.alb_sg.id]
  }

  load_balancer {
    target_group_arn = aws_lb_target_group.civitas_tg.arn
    container_name   = "web"
    container_port   = 8080
  }

  depends_on = [aws_lb_listener.http]
}

## Create an Auto Scaling Group for ECS Instances
resource "aws_launch_template" "ecs" {
  name          = "ecs-launch-template"
  image_id      = data.aws_ami.ecs_optimized.id
  instance_type = "t3.micro" # Change instance type if needed

  iam_instance_profile {
    name = aws_iam_instance_profile.ecs_instance_profile.name
  }

  user_data = base64encode(<<-EOF
    #!/bin/bash
    echo "ECS_CLUSTER=civitas-cluster" >> /etc/ecs/ecs.config
  EOF
  )

  network_interfaces {
    associate_public_ip_address = true
    security_groups             = [aws_security_group.ecs_sg.id]
  }
}

resource "aws_autoscaling_group" "ecs" {
  desired_capacity    = 1
  max_size            = 2
  min_size            = 1
  vpc_zone_identifier = var.subnet_ids

  launch_template {
    id      = aws_launch_template.ecs.id
    version = "$Latest"
  }
}

resource "aws_iam_role_policy_attachment" "ecs_ec2_policy" {
  role       = aws_iam_role.ecs_instance_role.name
  policy_arn = "arn:aws:iam::aws:policy/service-role/AmazonEC2ContainerServiceforEC2Role"
}

resource "aws_iam_instance_profile" "ecs_instance_profile" {
  name = "ecsInstanceProfile"
  role = aws_iam_role.ecs_instance_role.name
}

resource "aws_security_group" "ecs_sg" {
  name        = "ecs-instances-sg"
  description = "Allow inbound access from ALB and ECS tasks"

  ingress {
    from_port   = 8080
    to_port     = 8080
    protocol    = "tcp"
    cidr_blocks = ["0.0.0.0/0"] # Restrict to ALB CIDR if needed
  }

  egress {
    from_port   = 0
    to_port     = 0
    protocol    = "-1"
    cidr_blocks = ["0.0.0.0/0"]
  }
}

# Output Public ALB URL
output "alb_dns" {
  value = aws_lb.civitas_alb.dns_name
}
