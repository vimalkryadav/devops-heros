variable "aws_region" {
  description = "AWS region used for the short-lived assignment."
  type        = string
  default     = "us-east-1"
}

variable "operator_cidr" {
  description = "Current operator public IPv4 /32; only this address may reach the HTTP demo."
  type        = string
  validation {
    condition     = can(cidrhost(var.operator_cidr, 0)) && endswith(var.operator_cidr, "/32")
    error_message = "Provide a valid single-address IPv4 CIDR ending in /32."
  }
}
variable "vpc_cidr" {
  description = "Dedicated /16 network for the temporary lab."
  type        = string
  default     = "10.83.0.0/16"
  validation {
    condition     = can(cidrhost(var.vpc_cidr, 0)) && endswith(var.vpc_cidr, "/16")
    error_message = "Supply a valid IPv4 /16 CIDR."
  }
}
