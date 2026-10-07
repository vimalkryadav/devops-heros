# First apply: EC2 permissions and cleanup

Actual AWS run on 7 October 2026, 05:51–05:52 UTC, using Terraform 1.16.5 and AWS provider 6.67.0.

- [Validation](01-validation.txt) and the [plan](02-plan.txt) passed: 14 to add.
- [Apply](03-apply.txt) created 13 networking/storage resources, then the provider's
  `ec2:DescribeInstanceTypes` call failed. No instance was launched and HTTP verification did not run.
- The runner's `finally` block [destroyed all 13 resources](05-destroy.txt).
- [Terraform cleanup](cleanup.json) reports an empty state. The independent
  [AWS cleanup check](aws-cleanup-check.json) confirms that the bucket and VPC no longer exist
  and no Session 19 instance was found.
- [Complete terminal output](run.txt) retains the command failure and successful cleanup.

Subsequent read/dry-run checks also denied `ec2:DescribeVolumes`,
`ec2:DescribeInstanceCreditSpecifications`, `ec2:DescribeInstanceAttribute` and `ec2:RunInstances`.
The last two checks used a nonexistent instance ID and existing default networking respectively;
they do not prove authorization for future tagged assignment resources. Termination checks with
nonexistent IDs returned `InvalidInstanceID.Malformed`, so termination authorization remains unproven.

This is failure/cleanup evidence, not a completed Session 19 deployment. The runner now checks
the three unscoped instance/volume/credit read permissions before creating lab resources.
