## Launch Template for ECS
variable "instance_role" {
  default = ""
}
variable "ecs_cluster_name" {
  default = ""
}
resource "aws_launch_template" "ecs" {
  name          = "ecs-launch-template"
  image_id      = data.aws_ami.ecs_optimized.id
  instance_type = "t3.micro"

  iam_instance_profile {
    name = var.instance_role
  }

  user_data = base64encode(<<-EOF
    #!/bin/bash
    echo "ECS_CLUSTER=${var.ecs_cluster_name}" >> /etc/ecs/ecs.config
  EOF
  )

  network_interfaces {
    associate_public_ip_address = true
    security_groups             = [aws_security_group.ecs_sg.id]
  }
}

## Auto Scaling Group
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
