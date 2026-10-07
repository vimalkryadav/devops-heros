# DevOps assignments — Vimal Kumar Yadav, 24BCS10273

This README links every session's submission and its review PR. Sessions 1–7 were already in the central repository; their existing work was reviewed, and the Session 3 scripts were rerun. Sessions 8–20 have completed submissions. Session 21 reproduces both Docker deployment methods in Aryen's reference and includes tested CI, Kubernetes, monitoring and GitOps; its required EKS execution remains pending AWS permissions.

All new work uses `vimalyad`. The 13 central PRs and two standalone PRs remain open and unmerged. Sessions 16–17 use their required separate repositories; the other PRs target `vimalkryadav/devops-heros:main`. README links below point directly to submitted revisions, so they work before merge. Sessions 1–2 share the existing Linux submission.

| Session | Assignment README | Status | Review |
|---|---|---|---|
| 1–2 | [Linux foundations](https://github.com/vimalyad/devops-heros/blob/f14b772ccb378981830f5e384b245fa7d1779832/session2-linux/Vimal-24BCS10273/README.md) | Existing submission reviewed | Already on central main |
| 3 | [Shell scripting](https://github.com/vimalyad/devops-heros/blob/f14b772ccb378981830f5e384b245fa7d1779832/session3-shell-scripting/Vimal-24BCS10273/README.md) | Existing submission reviewed; scripts rerun | Already on central main |
| 4 | [Networking](https://github.com/vimalyad/devops-heros/blob/f14b772ccb378981830f5e384b245fa7d1779832/session4-networking/Vimal-24BCS10273/README.md) | Existing submission reviewed | Already on central main |
| 5 | [Git and GitHub](https://github.com/vimalyad/devops-heros/blob/f14b772ccb378981830f5e384b245fa7d1779832/session5-git-github/Vimal-24BCS10273/README.md) | Existing submission reviewed | Already on central main |
| 6 | [Docker fundamentals](https://github.com/vimalyad/devops-heros/blob/f14b772ccb378981830f5e384b245fa7d1779832/session6-7-docker/Vimal-24BCS10273/docker-fundamentals/README.md) | Existing submission reviewed | Already on central main |
| 7 | [Dockerfiles and images](https://github.com/vimalyad/devops-heros/blob/f14b772ccb378981830f5e384b245fa7d1779832/session6-7-docker/Vimal-24BCS10273/dockerfiles-and-images/README.md) | Existing submission reviewed | Already on central main |
| 8 | [Docker networking and volumes](https://github.com/vimalyad/devops-heros/blob/a29c19da03c62368510f981829784ba92b828373/session8-docker-networking-volume/Vimal-24BCS10273/README.md) | Completed and verified | [#10](https://github.com/vimalkryadav/devops-heros/pull/10) |
| 9 | [Kubernetes basics](https://github.com/vimalyad/devops-heros/blob/228f9db353d3ff2aaf6620be45b1bf073bbbdd20/session9-k8s/Vimal-24BCS10273/README.md) | Completed and verified | [#1](https://github.com/vimalkryadav/devops-heros/pull/1) |
| 10 | [Kubernetes core objects](https://github.com/vimalyad/devops-heros/blob/bbd0edf4a1ca62a67b41b28c7d8db2d4095b109d/session10-k8s-core-objects/Vimal-24BCS10273/README.md) | Completed and verified | [#2](https://github.com/vimalkryadav/devops-heros/pull/2) |
| 11 | [Kubernetes Services and DNS](https://github.com/vimalyad/devops-heros/blob/9ca46648f55450162005ef60a070cb3d0d8335bc/session-11-kubernetes-services/Vimal-24BCS10273/README.md) | Completed and verified | [#3](https://github.com/vimalkryadav/devops-heros/pull/3) |
| 12 | [Ingress, ConfigMaps and Secrets](https://github.com/vimalyad/devops-heros/blob/a24dc8d08a00588a9d498669bf1429ae0bc5e5a5/session-12-ingress-configmaps-secrets/Vimal-24BCS10273/README.md) | Completed and verified | [#4](https://github.com/vimalkryadav/devops-heros/pull/4) |
| 13 | [Storage, autoscaling and probes](https://github.com/vimalyad/devops-heros/blob/3d76a5914a445bf573f426e8fa39dc9230937b6f/session-13-storage-hpa-probes/Vimal-24BCS10273/README.md) | Completed and verified | [#5](https://github.com/vimalkryadav/devops-heros/pull/5) |
| 14 | [Kubernetes troubleshooting](https://github.com/vimalyad/devops-heros/blob/3750a93b5e5912fd59cfde1982bc4896ea6a405e/session-14-kubernetes-troubleshooting/Vimal-24BCS10273/README.md) | Completed and verified | [#6](https://github.com/vimalkryadav/devops-heros/pull/6) |
| 15 | [Helm](https://github.com/vimalyad/devops-heros/blob/b128a9f8d5d990d673eece61e009158eeede89e9/session-15-helm/Vimal-24BCS10273/README.md) | Completed and verified | [#7](https://github.com/vimalkryadav/devops-heros/pull/7) |
| 16 | [CI/CD](https://github.com/vimalyad/devops-cicd-demo/blob/446720279ce586475a7e3b87bd50d3132cdf8a6c/README.md) | Passing pipeline, failure gates, deployment and cleanup | [Standalone #1](https://github.com/vimalyad/devops-cicd-demo/pull/1) |
| 17 | [DevSecOps](https://github.com/vimalyad/devops-devsecops-demo/blob/46149ea14ee212e543aa745cbc3e22786e0f1a3c/README.md) | Passing scans, registry publication, deployment and cleanup | [Standalone #1](https://github.com/vimalyad/devops-devsecops-demo/pull/1) |
| 18 | [Terraform and AWS S3](https://github.com/vimalyad/devops-heros/blob/c4346826819f703a60a9c09db6313d551926b27c/session-18-terraform-aws/Vimal-24BCS10273/README.md) | Actual AWS apply, verification and destroy completed | [#9](https://github.com/vimalkryadav/devops-heros/pull/9) |
| 19 | [Cloud and Terraform](https://github.com/vimalyad/devops-heros/blob/478e85c947b4b6ae2b90336c4637b73c650ab346/session-19-cloud-terraform/Vimal-24BCS10273/README.md) | Six AWS network resources created, verified and destroyed | [#12](https://github.com/vimalkryadav/devops-heros/pull/12) |
| 20 | [Observability and GitOps](https://github.com/vimalyad/devops-heros/blob/23e0dc8f18355f3ef7dffc543314f5c0b0be13b5/session-20-observability-gitops/Vimal-24BCS10273/README.md) | Monitoring, alerts, reconciliation and cleanup verified | [#11](https://github.com/vimalkryadav/devops-heros/pull/11) |
| 21 | [Typeahead capstone](../session-21-final-devops-project/Vimal-24BCS10273/final-devops-project/README.md) | Direct Docker, Compose, CI and local Kubernetes verified; EKS pending | [Draft #13](https://github.com/vimalkryadav/devops-heros/pull/13) |

[Central PR #8](https://github.com/vimalkryadav/devops-heros/pull/8) also indexes the two standalone pipeline repositories and their tested revisions.

## Latest reference review

Aryen's assignments were reviewed at commit `bc73ce6b8663b92b8ac7310418fa5ac7f4c39afd` on 7 October 2026. Our implementations and execution evidence are in the linked submissions.

- **Session 19:** [Aryen's lab](https://github.com/aryen1101/Learn_DEVOPS/tree/bc73ce6b8663b92b8ac7310418fa5ac7f4c39afd/Class_Assignments/Cloud_and_Terraform_in_Action) provisions six network resources without EC2. Our matching lab actually created, verified and destroyed its VPC, subnet, internet gateway, route table, association and security group. Terraform state is empty, and independent AWS reads confirmed deletion. EC2/S3 were suggested architecture in this session's brief; Session 18 separately includes a completed S3 lifecycle.
- **Session 21:** [Aryen's final deployment](https://github.com/aryen1101/Learn_DEVOPS/blob/bc73ce6b8663b92b8ac7310418fa5ac7f4c39afd/Class_Assignments/Final_Deploy/Readme.md) demonstrates individual Docker containers and Compose. Both methods passed real health/readiness, CRUD, Kafka and search checks for Typeahead. This submission additionally includes a passing four-job pipeline, published/scanned images, local Kubernetes, monitoring, GitOps and a real 10m37s terminal recording. The reference's local screenshots do not establish EKS completion.

## Remaining capstone requirement

The [capstone requirement map](../session-21-final-devops-project/Vimal-24BCS10273/final-devops-project/REQUIREMENTS.md) records the outstanding cloud work. EKS and IAM reads and launch-template creation were still denied on 7 October; no capstone AWS resources were created. Terraform validation and its 21-resource plan passed, but a successful EKS apply, deployment verification and destroy are still needed for full cloud-module completion. PR #13 remains a draft for that reason.

The requested terminal-only format is applied to all 80 new screenshots. They capture real Bash PTYs through Playwright/CDP; visible terminal commands identify saved-log views. Browser and dashboard checks have real assertion/API records, while the rubric's specifically requested browser/console/dashboard images are not supplied under that format. The presentation guide and recorded release walkthrough are included; the final live presentation/submission remains with the student.

## Cleanup and evidence

Session 18's S3 lab, the earlier Session 19 partial attempts, and the final six-resource network lab were destroyed and checked for absence. The capstone's direct Docker, Compose, local Kubernetes and temporary CI deployments were cleaned up; the dedicated Minikube cluster is stopped. Nine unrelated containers retained their IDs. Each session README links its actual logs and screenshots. Existing screenshots from Sessions 1–7 remain historical evidence and are not described as fresh runs.
