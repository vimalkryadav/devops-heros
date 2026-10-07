# Temporary Terraform lab

Requires Terraform 1.16.x, the locked AWS provider, Python 3 and the dependencies in `../scripts/requirements.txt`. Configure an AWS profile outside this repository and export `AWS_PROFILE` and `AWS_REGION=us-east-1`.

```bash
python -m pip install -r ../scripts/requirements.txt
terraform init
terraform fmt -check
terraform validate
terraform plan -out=assignment.tfplan
terraform apply assignment.tfplan
terraform show
terraform output
terraform state list
terraform plan -destroy
terraform destroy
terraform state list
```

To execute the lab with verification and cleanup in a `finally` block, run `python ../scripts/run-lab.py`. The script owns only this project directory's state. It records commands, verifies the AWS resources, creates a destroy plan, applies it and runs an idempotent `terraform destroy`. Never import unrelated resources into this temporary lab.

The provider lock file is committed; `.terraform`, saved plans and local state are ignored. State maps resource addresses to real AWS IDs and may contain sensitive data, so it is not a public evidence artifact. Terraform references create dependencies; the graph determines creation order and reverses relevant dependencies for destruction.

`terraform.tfvars` contains only a region. Supply credentials through the external provider credential chain. Retain private state until AWS deletion has been verified. An interrupted CLI session does not itself remove resources: resume `terraform destroy` from this directory.

The complete command logs and verification records are stored under `../evidence/` after execution. Evidence describes observed outcomes, including failures if access is insufficient.

References: [Terraform workflow](https://developer.hashicorp.com/terraform/cli/run), [AWS provider](https://registry.terraform.io/providers/hashicorp/aws/6.67.0/docs), [S3 bucket resource](https://registry.terraform.io/providers/hashicorp/aws/6.67.0/docs/resources/s3_bucket).
