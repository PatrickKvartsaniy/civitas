variable "region" {
  description = "AWS region to create resources in"
  type        = string
  default     = "eu-west-3"
}

variable "repository_list" {
  description = "List of repository names"
  type        = list(any)
  default     = ["web", "etl"]
}

variable "subnet_ids" {
  description = "List of subnet IDs for the load balancer and ECS service"
  type        = list(string)
  default     = ["subnet-0105b61f08efc80ab", "subnet-040060eec8799d9f6", "subnet-00fe2557b94384005"]
}

variable "vpc_id" {
  description = "VPC ID where the load balancer and ECS service will be deployed"
  type        = string
  default     = "vpc-024d635b59d00a3fa"
}
