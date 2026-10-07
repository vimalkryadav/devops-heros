# Six-resource Terraform network lab

Use Terraform 1.16.x, the committed AWS provider lock, Python 3 and the dependencies in
`../scripts/requirements.txt`. AWS credentials stay in an external profile.

```bash
export AWS_PROFILE=YOUR_EXISTING_PROFILE
export AWS_REGION=us-east-1
export TF_VAR_operator_cidr=YOUR_PUBLIC_IPV4/32
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

The actual run planned, created and destroyed six managed resources: a VPC, public subnet,
internet gateway, route table, route-table association and security group. State also includes
the read-only availability-zone data source while the lab exists.

To execute with AWS assertions and automatic teardown, run `python3 ../scripts/run-lab.py`.
The runner uses this directory regardless of the shell's working directory and refuses an
existing nonempty state. It checks actual AWS resource relationships, tags, the default route,
web-port restrictions, and independent absence after destruction.

`aws_region` defaults to `us-east-1`; `vpc_cidr` defaults to `10.83.0.0/16`. The public subnet is
calculated from that CIDR. To try the reference's CIDR exercise, set `TF_VAR_vpc_cidr=10.10.0.0/16`
and run `terraform plan`; the subnet becomes `10.10.1.0/24`.

`.terraform`, local state, saved plans and private variable files are ignored. Do not import
unrelated infrastructure into this lab or delete the state before cleanup. A terminated shell
does not itself delete AWS resources; recover by running `terraform destroy` here.

[Terraform workflow](https://developer.hashicorp.com/terraform/cli/run),
[AWS provider](https://registry.terraform.io/providers/hashicorp/aws/6.67.0/docs).
