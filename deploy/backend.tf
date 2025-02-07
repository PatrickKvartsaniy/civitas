terraform {
  required_providers {
    docker = {
      source  = "kreuzwerker/docker"
      version = "3.0.2"
    }
  }
  cloud {
    organization = "terra-gis"
    workspaces {
      name = "base"
    }
  }
}
