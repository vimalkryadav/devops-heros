output "bucket_name" { value = aws_s3_bucket.assignment.id }
output "bucket_arn" { value = aws_s3_bucket.assignment.arn }
output "region" { value = var.aws_region }

output "vpc_id" { value = aws_vpc.lab.id }
output "subnet_id" { value = aws_subnet.public.id }
output "security_group_id" { value = aws_security_group.web.id }
output "instance_id" { value = aws_instance.web.id }
output "http_url" { value = "http://${aws_instance.web.public_ip}:8080" }
output "image_id" { value = data.aws_ami.linux.id }
