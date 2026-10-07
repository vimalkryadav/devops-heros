# Persistent web application with autoscaling and health checks

The course mini project combines a 500Mi RWO claim, two initial application replicas, a Service, CPU autoscaling between two and five replicas, and startup/readiness/liveness probes. This implementation uses a small Python HTTP server so `/work` can generate repeatable CPU load; its home page displays the saved student record and serving Pod name.

| File | Role |
| --- | --- |
| [namespace.yaml](namespace.yaml) | Isolates the lab in `assignment-s13`. |
| [pvc.yaml](pvc.yaml) | Requests dynamically provisioned storage. |
| [app.py](app.py), [app-config.yaml](app-config.yaml) | Application source and identical ConfigMap copy mounted into the container. |
| [deployment.yaml](deployment.yaml) | Two replicas, `/data` mount, resource requests/limits and all three probes. |
| [service.yaml](service.yaml) | Exposes HTTP on port 80 inside the namespace. |
| [hpa.yml](hpa.yml) | CPU target 50%, minimum two and maximum five replicas. |
| [load generator](../load-generator.yaml) | Four clients repeatedly request `/work`. |

Run `python3 run.py` from the parent student folder with the lab kubeconfig active. The runner applies the manifests, writes the student record, replaces a Pod, checks the replacement's UID and file, exercises probes, then adds and removes HTTP load. It records the real command output and stops on a failed check. Python uses only its standard library.

The readiness check returns 503 when `/tmp/unready` exists. The liveness check returns 503 when `/tmp/unhealthy` exists. Removing the readiness marker restores traffic without restarting the process. The liveness marker is in the container's writable layer, so a replacement container starts without it. The server deliberately delays startup by eight seconds; the startup probe allows up to sixty seconds before treating initialization as failed.

CPU is requested at 100m per application container and limited to 250m. The HPA's 50% target is relative to the CPU request, so it corresponds to roughly 50m per replica. This is unrelated to 50% of the whole node. The scale-down stabilization window is explicitly shortened to sixty seconds for this local exercise. See the [HPA behavior documentation](https://kubernetes.io/docs/concepts/workloads/autoscaling/horizontal-pod-autoscale/).

The CPU-intensive endpoint and file-based fault switches are learning aids. The shared RWO claim also assumes a single node; see the [storage notes](../01-kubernetes-volumes/README.md). This demonstration does not establish a production-ready, multi-node service.

The original brief is the instructor's [session 13 mini project](https://github.com/Nency-Ravaliya/devops-heros/blob/main/session-13-storage-hpa-probes/mini-project/README.md).
