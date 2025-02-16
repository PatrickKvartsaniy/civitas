module "ecr" {
  source = "./ecr"
}

module "ecs" {
  source        = "./ecs"
  subnet_ids    = var.subnet_ids
  vpc_id        = var.vpc_id
  alb_sg_id     = module.networking.alb_sg_id
  alb_tg_arn    = module.networking.alb_tg_arn
  docker_images = module.ecr.docker_images
}

module "iam" {
  source = "iam"
}

module "networking" {
  source     = "networking"
  vpc_id     = var.vpc_id
  subnet_ids = var.subnet_ids
}

module "autoscaling" {
  source           = "autoscaling"
  subnet_ids       = var.subnet_ids
  ecs_cluster_name = module.ecs.cluster_name
  instance_role    = module.iam.instance_role
}
