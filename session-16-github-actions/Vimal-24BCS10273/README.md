# Session 16: Rollout Planner CI/CD

Vimal Kumar Yadav · 24BCS10273

This assignment has its own repository so GitHub Actions runs from that repository's root. This central submission links to the implementation and evidence.

- [Repository](https://github.com/vimalyad/devops-cicd-demo)
- [Implementation PR #1](https://github.com/vimalyad/devops-cicd-demo/pull/1)
- [Complete README at the submitted revision](https://github.com/vimalyad/devops-cicd-demo/blob/67bd3b2aab01b16208db2f705010cb401aa526e6/README.md)
- [Execution reports and terminal-only screenshots](https://github.com/vimalyad/devops-cicd-demo/blob/67bd3b2aab01b16208db2f705010cb401aa526e6/evidence/README.md)

The Go API calculates rollout batches. Its pipeline compiles, vets and tests the code, builds a non-root image, deploys two replicas to a temporary kind cluster, verifies HTTP responses and deletes the cluster.

| Demonstration | Run |
| --- | --- |
| Successful implementation | [37518285500](https://github.com/vimalyad/devops-cicd-demo/actions/runs/37518285500) |
| Intentional failure blocks later jobs | [37518538812](https://github.com/vimalyad/devops-cicd-demo/actions/runs/37518538812) |
| Corrected exercise passes | [37519385191](https://github.com/vimalyad/devops-cicd-demo/actions/runs/37519385191) |

The real Bash terminal screenshots show live GitHub queries, local tests, or visible commands inspecting retained run reports. Temporary clusters were deleted after verification. The deployment is ephemeral and uses no AWS resources.
