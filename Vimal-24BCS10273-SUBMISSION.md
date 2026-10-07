# DevOps submissions — Vimal Kumar Yadav, 24BCS10273

All new work is submitted through PRs from `vimalyad`; PRs remain unmerged. Sessions 16–17 use their required standalone repositories. The other additions target this central repository.

| Sessions | Submission |
|---|---|
| 1–7 | Existing central submissions reviewed; session 3 scripts rerun in isolation |
| 8 | [PR #10](https://github.com/vimalkryadav/devops-heros/pull/10) — Docker/networking corrections |
| 9 | [PR #1](https://github.com/vimalkryadav/devops-heros/pull/1) — Kubernetes Basics |
| 10 | [PR #2](https://github.com/vimalkryadav/devops-heros/pull/2) — rollout strategies and pod lifecycle |
| 11 | [PR #3](https://github.com/vimalkryadav/devops-heros/pull/3) — resources, DNS and LoadBalancer |
| 12 | [PR #4](https://github.com/vimalkryadav/devops-heros/pull/4) — Ingress and Secrets |
| 13 | [PR #5](https://github.com/vimalkryadav/devops-heros/pull/5) — storage, probes and HPA |
| 14 | [PR #6](https://github.com/vimalkryadav/devops-heros/pull/6) — troubleshooting and mini project |
| 15 | [PR #7](https://github.com/vimalkryadav/devops-heros/pull/7) — Helm |
| 16 | [CI/CD PR](https://github.com/vimalyad/devops-cicd-demo/pull/1) — passing pipeline, failure gates, kind deployment/cleanup |
| 17 | [DevSecOps PR](https://github.com/vimalyad/devops-devsecops-demo/pull/1) — enforced scans, GHCR, deployment/cleanup |
| 16–17 index | [Central PR #8](https://github.com/vimalkryadav/devops-heros/pull/8) — links and exact workflow revisions |
| 18 | [PR #9](https://github.com/vimalkryadav/devops-heros/pull/9) — actual S3 apply/verify/destroy and service research |
| 19 | [Draft PR #12](https://github.com/vimalkryadav/devops-heros/pull/12) — Terraform cloud lab; successful EC2 run remains blocked |
| 20 | [PR #11](https://github.com/vimalkryadav/devops-heros/pull/11) — observability, alerts, GitOps and cleanup |
| 21 | [Typeahead capstone](session-21-final-devops-project/Vimal-24BCS10273/final-devops-project/README.md) — implementation, evidence and remaining requirements |

Session 19 needs the eligible `t4g.micro` type allowed by the installed launch policy. Both failed partial attempts were destroyed, and AWS absence checks passed. The capstone additionally needs scoped EKS/IAM/launch-template access and a real EKS apply/verify/destroy cycle. Its local and CI deployments do not replace the required cloud execution.

New screenshots show only actual terminals captured from spawned PTYs with Playwright/CDP. The capstone's explicit browser/console/dashboard screenshot requirements remain pending a format decision. Its [requirement map](session-21-final-devops-project/Vimal-24BCS10273/final-devops-project/REQUIREMENTS.md) distinguishes completed checks from pending work.
