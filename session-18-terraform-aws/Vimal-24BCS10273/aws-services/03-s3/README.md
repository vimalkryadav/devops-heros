# S3: object storage

S3 stores objects identified by keys inside buckets. It suits static assets, backups, logs and data lakes; it is not an attached block device or a normal shared filesystem.

| Feature | Use and tradeoff |
| --- | --- |
| Bucket | A regional container for objects and bucket-level settings. This lab lets Terraform generate a unique name. |
| Object | Data plus metadata addressed by a key; prefixes organize keys without creating filesystem directories. |
| Storage classes | Standard for frequent access; Intelligent-Tiering for changing access patterns; infrequent-access and archival classes for different retrieval and retention needs. Compare retrieval charges and minimum durations. |
| Versioning | Retains multiple versions and supports recovery; old versions also consume storage. A delete marker does not erase historical versions. |
| Lifecycle | Rules transition or expire matching objects and optionally noncurrent versions. |
| Encryption | SSE-S3 uses S3-managed encryption keys; SSE-KMS adds KMS controls, permissions and potential request/key charges. |
| Bucket policy | A resource policy granting or denying actions for principals, resources and conditions. |

The Terraform bucket blocks public access, disables ACL-based ownership through BucketOwnerEnforced and explicitly selects SSE-S3. This temporary lab keeps versioning disabled and does not create archival copies. No public-read policy is needed.

Sources: [S3 overview](https://docs.aws.amazon.com/AmazonS3/latest/userguide/Welcome.html), [storage classes](https://docs.aws.amazon.com/AmazonS3/latest/userguide/storage-class-intro.html), [versioning](https://docs.aws.amazon.com/AmazonS3/latest/userguide/Versioning.html), [encryption](https://docs.aws.amazon.com/AmazonS3/latest/userguide/UsingServerSideEncryption.html).
