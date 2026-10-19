# Nginx diagnosis mini project

The [application manifests](../manifests/web.yaml) create a two-replica Nginx Deployment, a ClusterIP Service and a BusyBox client. The runner first verifies localhost HTTP inside Nginx, reads logs and inspects the Service. It then diagnoses a separate broken-image Pod and deliberately changes the Service selector.

```text
BusyBox client -> troubleshooting-service:80
                           |
                app=troubleshooting-app
                      /          \
                  Nginx Pod    Nginx Pod
```

## Broken Pod answers

1. **Status:** `ErrImagePull` followed by `ImagePullBackOff`; both were captured before applying the fix.
2. **Actual error:** the container runtime could not resolve `docker.io/library/nginx:assignment-tag-does-not-exist`; the registry returned `not found`.
3. **Useful command:** `kubectl describe pod project-broken-pod` showed the image and pull events. `kubectl events --for pod/project-broken-pod` isolated those events.
4. **Image problem:** the repository existed, but the requested tag did not.
5. **Fix:** apply [image-fixed.yaml](../cases/image-fixed.yaml), which uses `nginx:1.27-alpine`, then wait for readiness and make a real HTTP request.

See the [complete before/after evidence](../evidence/01-image.txt).

## Troubleshooting table

| Problem | What I saw | Command | Cause | Fix |
| --- | --- | --- | --- | --- |
| Broken Pod | No ready container; repeated pull attempts | `get pod`, `describe pod` | Invalid image tag | Select the available tag and wait for readiness |
| Service problem | Empty EndpointSlice, then HTTP connection failure | `get endpointslices`, `get pods --show-labels`, `describe service` | Selector `wrong-app` matched no Pod | Restore `app=troubleshooting-app` and verify both endpoints and HTTP |
| Image problem | Runtime `not found` error | `events --for pod/project-broken-pod` | Image reference named an unpublished tag | Correct that reference; no cluster restart was needed |

The broken-Pod and image rows describe the same injected image fault. They are not presented as separate runs.

## Command and concept questions

1. **What does `get` tell us?** It summarizes the current API objects. For Pods, the default columns show readiness, container status, restart count and age.
2. **How is `describe` different?** It expands one object's settings, conditions, container states and related events. It explains many failures hidden by the summary view.
3. **Why use `logs`?** Scheduling can succeed while the program itself fails. Logs reveal application messages; `--previous` helps after a container restart.
4. **When use `exec`?** To inspect a running container's files, environment, DNS configuration or connectivity from its own network context.
5. **What is CrashLoopBackOff?** The container keeps terminating and Kubernetes delays the next restart. Investigate its exit reason and logs; the backoff is a symptom.
6. **What is ImagePullBackOff?** Image retrieval failed and the next attempt is delayed. Tags, credentials and network access are possible causes; our event identified a missing tag.
7. **Why Pending?** A Pod has not completed startup. It may be unschedulable or still preparing containers and volumes. Our scheduler example could not match its node selector.
8. **Why no Service endpoints?** Common causes include a selector mismatch or unavailable/unready backends. Check the labels and ready conditions, not just whether a Service object exists.
9. **How do selectors relate to labels?** A selector chooses Pods whose labels match its requirements. Our repaired selector selected two Nginx Pods.
10. **What is Kubernetes DNS?** Cluster DNS lets workloads find Services by names. The DNS case showed that a bad Pod resolver can fail even while the cluster resolver works for other Pods.

`CrashLoopBackOff` and `ContainerCreating` are container waiting reasons shown by kubectl; they are not Pod API phases. The mount-failure Pod's actual phase was `Pending` while its displayed container status was `ContainerCreating`.
