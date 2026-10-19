output "bucket_name" { value = aws_s3_bucket.assignment.id }
output "bucket_arn" { value = aws_s3_bucket.assignment.arn }
output "region" { value = var.aws_region }
