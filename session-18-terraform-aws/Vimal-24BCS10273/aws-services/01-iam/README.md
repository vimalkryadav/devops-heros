# IAM: identities and permissions

IAM controls who can request actions on AWS resources. Authentication establishes the identity; authorization evaluates whether its requested action is permitted.

| Concept | Purpose and example |
| --- | --- |
| User | An identity within an account; may have console credentials or access keys. |
| Group | Collects users sharing permissions, such as read-only developers. Roles cannot join groups. |
| Role | An assumable identity that issues temporary credentials; suitable for EC2 workloads or federated users. |
| Policy | A JSON permission document containing effects, actions, resources and optional conditions. |
| Permissions | The resulting access after applicable policies and controls are evaluated. An explicit deny overrides an allow. |

Least privilege means granting only required actions on required resources. A deployment identity may create a particular project's infrastructure while an application role only reads its own bucket objects. Neither needs account administration.

Prefer federation and temporary role credentials; protect human access with MFA, avoid routine root use, remove unused permissions, and inspect audit activity. Never put credentials in source code, Terraform variables, state screenshots or Git history. This lab reads an external credential profile through the normal provider chain.

Sources: [IAM overview](https://docs.aws.amazon.com/IAM/latest/UserGuide/introduction.html), [security best practices](https://docs.aws.amazon.com/IAM/latest/UserGuide/best-practices.html), [policy evaluation](https://docs.aws.amazon.com/IAM/latest/UserGuide/reference_policies_evaluation-logic.html).
