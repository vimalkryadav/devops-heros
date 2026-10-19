terraform {
  required_version = "~> 1.16.0"
  required_providers {
    aws = { source = "hashicorp/aws", version = "= 6.67.0" }
  }
}
provider "aws" {
  region = var.aws_region
  default_tags {
    tags = { Project = "devops-assignment", Owner = "Vimal-24BCS10273", Session = "19", ManagedBy = "Terraform" }
  }
}
