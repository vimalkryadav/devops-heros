# DynamoDB and RDS: database choices

## DynamoDB

DynamoDB is a managed NoSQL database organized into tables, items and attributes. Every item has a primary key: a partition key alone, or a partition key plus a sort key. The partition key determines placement; the sort key orders related items within that key. Plan access patterns and indexes before choosing keys. A badly distributed key can concentrate traffic.

For example, a search-history table could use `user_id` as its partition key and a timestamp-plus-identifier as its sort key. Session storage, carts and predictable key-based application access are common uses. Relational joins are not its core access model.

## RDS

RDS manages relational database instances, including engines such as PostgreSQL, MySQL, MariaDB, Oracle and SQL Server; engine availability and options vary. SQL tables, constraints and transactions suit applications needing relationships and flexible queries.

Place database instances in suitable subnets, restrict security-group access to the application, encrypt storage and connections, and control database accounts. Automated backups support recovery within the configured retention window; snapshots offer separately managed recovery points.

Multi-AZ deployments improve availability and failover. Read replicas primarily serve read scaling and related recovery use cases; asynchronous replication may lag. A classic Multi-AZ DB-instance standby is not a readable replica. Multi-AZ DB clusters have different reader capabilities.

The course's research task does not require provisioning either service. The capstone uses PostgreSQL inside its temporary cluster, avoiding an additional managed-database bill.

Sources: [DynamoDB introduction](https://docs.aws.amazon.com/amazondynamodb/latest/developerguide/Introduction.html), [DynamoDB components](https://docs.aws.amazon.com/amazondynamodb/latest/developerguide/HowItWorks.CoreComponents.html), [RDS overview](https://docs.aws.amazon.com/AmazonRDS/latest/UserGuide/Welcome.html), [Multi-AZ](https://docs.aws.amazon.com/AmazonRDS/latest/UserGuide/Concepts.MultiAZ.html), [read replicas](https://docs.aws.amazon.com/AmazonRDS/latest/UserGuide/USER_ReadRepl.html).
