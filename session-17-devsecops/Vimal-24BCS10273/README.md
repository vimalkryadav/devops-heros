# Session 17: Release Catalog DevSecOps

Vimal Kumar Yadav · 24BCS10273

This assignment has its own repository so GitHub Actions runs from that repository's root. This central submission links to the implementation and evidence.

- [Repository](https://github.com/vimalyad/devops-devsecops-demo)
- [Implementation PR #1](https://github.com/vimalyad/devops-devsecops-demo/pull/1)
- [Complete README at the submitted revision](https://github.com/vimalyad/devops-devsecops-demo/blob/271dfd3c2bad3fe2f056cbefa124f34e1a5f045c/README.md)
- [Execution reports and terminal-only screenshots](https://github.com/vimalyad/devops-devsecops-demo/blob/271dfd3c2bad3fe2f056cbefa124f34e1a5f045c/evidence/README.md)

The Go CRUD API passes application tests, SAST, SCA, secret scanning and an image vulnerability gate before GHCR publication and Kubernetes deployment. The published image was retrieved and its CRUD behavior verified in a temporary kind cluster.

| Demonstration | Run |
| --- | --- |
| Successful implementation | [37518286603](https://github.com/vimalyad/devops-devsecops-demo/actions/runs/37518286603) |
| Intentional failure blocks later jobs | [37518538012](https://github.com/vimalyad/devops-devsecops-demo/actions/runs/37518538012) |
| Corrected exercise passes | [37519400322](https://github.com/vimalyad/devops-devsecops-demo/actions/runs/37519400322) |

The real Bash terminal screenshots show live GitHub queries, local tests, or visible commands inspecting retained run reports. Temporary clusters were deleted after verification. The deployment is ephemeral and uses no AWS resources.
