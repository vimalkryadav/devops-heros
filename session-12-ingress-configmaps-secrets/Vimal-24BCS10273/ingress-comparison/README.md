# Ingress and its controller

| | Ingress | Ingress controller |
| --- | --- | --- |
| What it is | A Kubernetes API object describing HTTP/HTTPS routing | Software that watches routing objects and configures a proxy/load balancer |
| Main responsibility | Declare hostnames, paths, backend Services and TLS Secret references | Make matching rules work in the data plane |
| Where to inspect it | `kubectl get ingress -A` and `kubectl describe ingress` | Controller Deployment/Pods, logs, Service and its external access path |
| Selected by | `spec.ingressClassName` | An `IngressClass` whose controller identifier it handles |
| Example | `campus.local/api` routes to the campus backend Service | Traefik, HAProxy or AWS Load Balancer Controller handling that class |

Creating an Ingress object alone does not start a proxy, open a port or create DNS
records. A matching controller must be installed and reachable. Conversely, an
installed controller needs routing configuration to know which application should
receive a request. A default backend may answer unmatched requests, often with 404.

For the earlier lab, the request path is:

```text
browser → controller's reachable address → matching host/path rule
        → backend Service's ready endpoints → application Pod
```

DNS resolves the hostname to the controller's access point. The HTTP Host header
and URL path select the route; TLS SNI also selects a certificate/virtual host.
Controllers differ in whether they forward through a Service IP or directly to
its endpoints. Readiness and the Service selector must be correct in either case.

The earlier nginx lab uses annotations for rewrite behavior; these annotations
are controller-specific, unlike the core Ingress API fields. Ingress does not
replace ConfigMaps, Secrets or Services: it references or depends on them. TLS
private keys belong in a Secret or an external secret system, never in the public
assignment repository.

The Ingress API is stable but frozen; Kubernetes recommends Gateway API for new
routing capabilities. This assignment retains Ingress because the homework
explicitly asks for it. The existing screenshots document their original local
nginx-controller run and are not a claim about a fresh controller installation.

Reference: [Kubernetes Ingress](https://kubernetes.io/docs/concepts/services-networking/ingress/).
