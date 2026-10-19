# Kubernetes object comparisons

## Deployment and ReplicaSet

| Question | Deployment | ReplicaSet |
| --- | --- | --- |
| Purpose | Manage a versioned application and its rollout | Maintain a count of matching Pods |
| Pod management | Creates ReplicaSets; they create the Pods | Creates replacement Pods when replicas are missing |
| Scaling | Change `spec.replicas` or use `kubectl scale deployment` | Change `spec.replicas`, usually through its owning Deployment |
| Image change | Creates a new ReplicaSet and moves replicas between versions | Changing its template does not replace existing Pods |
| Rolling updates | Controls `maxSurge`, `maxUnavailable`, rollout history and rollback | Has no rollout strategy or revision management |

The normal ownership chain is `Deployment → ReplicaSet → Pod`. Manually scaling a
Deployment-owned ReplicaSet competes with the Deployment controller. Scale the
Deployment instead. A standalone ReplicaSet is useful for learning the controller,
but a Deployment is usually the right object for a stateless application.

## Deployment, DaemonSet and StatefulSet

| Property | Deployment | DaemonSet | StatefulSet |
| --- | --- | --- | --- |
| Typical application | Stateless web/API service | Node agent such as a log collector | Database or other stateful service |
| Pod creation | Interchangeable Pods through ReplicaSets | A Pod on each eligible node | Pods with stable ordinal names, such as `db-0` |
| Scaling | Set a replica count or attach an HPA | Count follows eligible nodes and placement rules | Set a replica count; default creation/deletion is ordered |
| Networking | A Service selects any ready replica | May expose node-local ports or use a Service | A headless Service supplies stable per-Pod DNS identities |
| Storage | Optional volumes/PVCs; no automatic claim per replica | Often mounts node paths for agent data | `volumeClaimTemplates` creates separate claims per ordinal |
| Example | Three campus API replicas | A log collector on every worker | PostgreSQL with deliberate database replication configuration |

A StatefulSet supplies identity and storage attachment, not database replication
or backups. Application-level replication still needs configuration. PVC retention
depends on the StatefulSet retention policy; inspect it before deleting a lab.

## ReplicaSet and Service

A ReplicaSet keeps Pods present. A Service makes them reachable through a stable
virtual IP/name while their individual IPs change. Both use labels, but a Service
does not own, create, restart or scale Pods. Its selector can match Pods from
several ReplicaSets, as in a canary experiment.

For a normal ClusterIP Service, the EndpointSlice controller tracks selected Pods
and their readiness. A client resolves the Service name, sends traffic to the
Service IP and port, and the cluster's Service implementation forwards it to a
ready endpoint's `targetPort`. In this Minikube lab kube-proxy provides that data
path. DNS and packet forwarding are separate steps: successful DNS does not prove
that the selector, readiness or target port is correct.

References: [Deployment](https://kubernetes.io/docs/concepts/workloads/controllers/deployment/),
[ReplicaSet](https://kubernetes.io/docs/concepts/workloads/controllers/replicaset/),
[DaemonSet](https://kubernetes.io/docs/concepts/workloads/controllers/daemonset/),
[StatefulSet](https://kubernetes.io/docs/concepts/workloads/controllers/statefulset/),
[Service](https://kubernetes.io/docs/concepts/services-networking/service/).
