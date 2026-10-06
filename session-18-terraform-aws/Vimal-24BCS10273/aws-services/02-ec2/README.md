# EC2: virtual compute

EC2 supplies virtual servers. Web applications, build workers and short-lived experiments are common uses.

| Concept | Meaning |
| --- | --- |
| AMI | A regional machine image containing the operating system and boot configuration. Its architecture must match the instance type. |
| Instance type | CPU, memory and networking capacity; select from measured workload needs. |
| Key pair | Public/private keys used for supported login methods. Keep the private key outside Git; an instance need not expose SSH. |
| Security group | Stateful allow rules attached to network interfaces. Restrict sources and ports. |
| EBS | Persistent block storage. Its lifecycle and charges are separate from instance compute; configure deletion where intended. |
| Private IP | Address used inside the VPC and connected networks. |
| Public IP | Publicly routable address; connectivity still needs routes and security rules. Public IPv4 has a separate charge. |

The usual lifecycle is pending → running → stopping → stopped, or shutting-down → terminated. Stopping preserves an EBS-backed instance for restart; termination removes the instance. Retained volumes can continue costing money. Auto-assigned public IPv4 can change after stopping and restarting.

Session 19 uses a small ARM Linux instance, an encrypted root volume and restricted HTTP access. Terraform destroys it after verification.

Sources: [EC2 concepts](https://docs.aws.amazon.com/AWSEC2/latest/UserGuide/concepts.html), [instance lifecycle](https://docs.aws.amazon.com/AWSEC2/latest/UserGuide/ec2-instance-lifecycle.html), [IP addressing](https://docs.aws.amazon.com/AWSEC2/latest/UserGuide/using-instance-addressing.html).
