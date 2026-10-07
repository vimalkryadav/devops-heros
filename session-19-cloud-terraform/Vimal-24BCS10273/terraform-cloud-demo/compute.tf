data "aws_availability_zones" "available" { state = "available" }
data "aws_ami" "linux" {
  most_recent = true
  owners      = ["amazon"]
  filter {

    name = "name"

    values = ["al2023-ami-2023.*-kernel-6.1-arm64"]

  }
  filter {

    name = "architecture"

    values = ["arm64"]

  }
  filter {

    name = "state"

    values = ["available"]

  }
}
resource "aws_vpc" "lab" {
  cidr_block           = "10.83.0.0/16"
  enable_dns_support   = true
  enable_dns_hostnames = true
  tags                 = { Name = "vimal-session19" }
}
resource "aws_subnet" "public" {
  vpc_id                  = aws_vpc.lab.id
  cidr_block              = "10.83.1.0/24"
  availability_zone       = data.aws_availability_zones.available.names[0]
  map_public_ip_on_launch = true
}
resource "aws_internet_gateway" "lab" { vpc_id = aws_vpc.lab.id }
resource "aws_route_table" "public" {
  vpc_id = aws_vpc.lab.id
  route {

    cidr_block = "0.0.0.0/0"

    gateway_id = aws_internet_gateway.lab.id

  }
}
resource "aws_route_table_association" "public" {
  subnet_id      = aws_subnet.public.id
  route_table_id = aws_route_table.public.id
}
resource "aws_security_group" "web" {
  name_prefix = "vimal-session19-"
  description = "Assignment HTTP access restricted to the operator address"
  vpc_id      = aws_vpc.lab.id
}
resource "aws_vpc_security_group_ingress_rule" "http" {
  security_group_id = aws_security_group.web.id
  cidr_ipv4         = var.operator_cidr
  ip_protocol       = "tcp"
  from_port         = 8080
  to_port           = 8080
}
resource "aws_vpc_security_group_egress_rule" "outbound" {
  security_group_id = aws_security_group.web.id
  cidr_ipv4         = "0.0.0.0/0"
  ip_protocol       = "-1"
}
resource "aws_instance" "web" {
  ami                                  = data.aws_ami.linux.id
  instance_type                        = var.instance_type
  subnet_id                            = aws_subnet.public.id
  vpc_security_group_ids               = [aws_security_group.web.id]
  associate_public_ip_address          = true
  instance_initiated_shutdown_behavior = "terminate"
  user_data                            = file("${path.module}/bootstrap.sh")
  user_data_replace_on_change          = true
  credit_specification { cpu_credits = "standard" }
  metadata_options { http_tokens = "required" }
  root_block_device {
    volume_size           = 8
    volume_type           = "gp3"
    encrypted             = true
    delete_on_termination = true
  }
  depends_on = [aws_route_table_association.public]
  tags       = { Name = "vimal-session19-http" }
}
resource "aws_s3_object" "record" {
  bucket                 = aws_s3_bucket.assignment.id
  key                    = "assignment.txt"
  content                = "Session 19: Vimal Kumar Yadav, 24BCS10273\n"
  server_side_encryption = "AES256"
}
