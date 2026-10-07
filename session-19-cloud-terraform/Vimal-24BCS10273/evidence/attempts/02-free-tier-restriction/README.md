> Historical expanded-compute attempt. The final submission is the successfully executed six-resource network lab in the [main README](../../../README.md).

# Second apply: account Free Tier restriction

Actual AWS run on 7 October 2026, after the required EC2 read permissions were added.

[Access checks](00-access-check.txt), [validation](01-validation.txt) and the
[14-resource plan](02-plan.txt) passed. [Apply](03-apply.txt) reached `RunInstances`, but AWS
returned `InvalidParameterCombination`: t4g.nano was not eligible for this account's Free Tier.
No EC2 instance was launched. The runner [destroyed all 13 created resources](05-destroy.txt),
left [empty state](cleanup.json), and the independent [AWS check](aws-cleanup-check.json)
confirmed bucket/VPC deletion and no Session 19 instance. [Full output](run.txt) is retained.

An explicit DescribeInstanceTypes request confirmed `FreeTierEligible=true` for t4g.micro.
The configuration now selects that ARM instance. The IAM launch condition also needs to change
from t4g.nano to t4g.micro; the account has not been upgraded or had its billing plan changed.
