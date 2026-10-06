resource "aws_s3_bucket" "assignment" {
  bucket_prefix = "vimal-24bcs10273-s18-"
  force_destroy = false
}
resource "aws_s3_bucket_public_access_block" "assignment" {
  bucket                  = aws_s3_bucket.assignment.id
  block_public_acls       = true
  block_public_policy     = true
  ignore_public_acls      = true
  restrict_public_buckets = true
}
resource "aws_s3_bucket_ownership_controls" "assignment" {
  bucket = aws_s3_bucket.assignment.id
  rule { object_ownership = "BucketOwnerEnforced" }
}
resource "aws_s3_bucket_server_side_encryption_configuration" "assignment" {
  bucket = aws_s3_bucket.assignment.id
  rule {
    apply_server_side_encryption_by_default { sse_algorithm = "AES256" }
  }
}
