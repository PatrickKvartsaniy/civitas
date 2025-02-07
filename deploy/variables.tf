variable "region" {
  description = "AWS region to create resources in"
  type  = string
  default = "eu-west-3"
}

variable "repository_list" {
  description = "List of repository names"
  type = list(any)
  default = ["web", "etl"]
}

variable "backend_container_port" {
  type        = number
  description = "Backend container port"
  default     = 8000
}
