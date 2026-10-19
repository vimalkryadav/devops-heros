# VPC: network boundaries and routing

A VPC is an isolated virtual network with an IP range expressed as CIDR. For example, `10.83.0.0/16` can contain `10.83.1.0/24` as a subnet. A subnet belongs to one Availability Zone.

| Component | Purpose |
| --- | --- |
| Route table | Chooses the next hop for destination ranges. The most specific matching route wins. |
| Internet Gateway | Connects an attached VPC to the internet; IPv4 instances also need a public address and permitted traffic. |
| NAT Gateway | Lets private IPv4 workloads initiate outbound connections while translating addresses. It adds hourly and processing charges. |
| Security group | Stateful allow rules for network interfaces; return traffic for permitted connections is tracked. |
| Network ACL | Stateless subnet-level allow/deny rules; request and return paths must both be allowed. |
| Public subnet | Has a route to an Internet Gateway. A route alone does not make every resource accessible. |
| Private subnet | Has no direct route to an Internet Gateway; outbound access may use NAT or appropriate service endpoints. |

Session 19 uses one public subnet and permits HTTP only from the operator's `/32`. The short lab does not need NAT. Production isolation and availability requirements may justify a different design.

Sources: [VPC overview](https://docs.aws.amazon.com/vpc/latest/userguide/what-is-amazon-vpc.html), [route tables](https://docs.aws.amazon.com/vpc/latest/userguide/VPC_Route_Tables.html), [security](https://docs.aws.amazon.com/vpc/latest/userguide/VPC_Security.html).
