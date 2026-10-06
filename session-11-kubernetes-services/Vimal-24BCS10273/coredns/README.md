# CoreDNS and Service discovery

CoreDNS is a DNS server with a plugin-based configuration. In this cluster it runs
as a Deployment in `kube-system`, reached through the `kube-dns` Service on UDP/TCP
port 53. Kubernetes uses it to translate Service names into addresses without
hard-coding Pod IPs into applications.

For `catalog.assignment-s11.svc.cluster.local.`, the client sends a DNS query to
its configured nameserver. CoreDNS's `kubernetes` plugin answers from Kubernetes
Service/EndpointSlice information. The reply is the Service ClusterIP for a normal
Service. The subsequent HTTP request travels through the Service data path;
CoreDNS is not an HTTP proxy. Names outside the cluster domain are normally sent
to upstream resolvers through `forward`.

## Configuration

Inspect the running configuration, Pods and Service:

```bash
kubectl -n kube-system get configmap coredns -o yaml
kubectl -n kube-system get deployment coredns
kubectl -n kube-system get pods -l k8s-app=kube-dns -o wide
kubectl -n kube-system get service kube-dns
kubectl -n kube-system get endpointslices -l kubernetes.io/service-name=kube-dns
kubectl -n kube-system logs deployment/coredns --tail=30
```

The ConfigMap's `Corefile` is a server block and ordered plugin configuration. The
lab captures the installed configuration rather than applying a replacement.

| Directive/plugin | Role |
| --- | --- |
| `.:53` | Listen on port 53 for the root zone |
| `errors` | Log processing errors |
| `health`, `ready` | Health/readiness endpoints |
| `kubernetes cluster.local ...` | Answer cluster Service and reverse-zone queries |
| `prometheus :9153` | Export DNS metrics |
| `forward . /etc/resolv.conf` | Forward unmatched queries upstream |
| `cache` | Cache responses for the configured TTL |
| `loop` | Detect simple forwarding loops |
| `reload` | Reload changed configuration |
| `loadbalance` | Vary the ordering of multiple answer records |

These names describe common CoreDNS plugins; the actual captured Corefile is the
authority for which ones this lab enables.

## Troubleshooting order

1. Check the caller's namespace, `/etc/resolv.conf`, `dnsPolicy` and spelling. Test
   both the short name and the absolute name using `nslookup` inside that Pod.
2. Confirm the Service exists in the intended namespace. `NXDOMAIN` for a short
   name in the wrong namespace can be correct DNS behavior.
3. Query `kubernetes.default.svc.cluster.local.`. If that also times out, inspect
   CoreDNS readiness, the `kube-dns` Service/endpoints and UDP/TCP 53 connectivity.
4. Inspect CoreDNS logs and the Corefile. `SERVFAIL` can indicate resolution or
   configuration failures; a timeout instead suggests reachability or an
   unresponsive DNS server. Also check NetworkPolicies and the CNI.
5. If DNS resolves but HTTP fails, inspect application readiness, EndpointSlices,
   Service selectors and `targetPort`. That problem may be outside DNS.

The [recorded lab](../dns-lab/evidence/dns.txt) demonstrates a real namespace
lookup failure and its fix, followed by successful HTTP access. No cluster DNS
configuration was changed. Cleanup removes only the two lab namespaces.

Reference: [Debugging DNS resolution](https://kubernetes.io/docs/tasks/administer-cluster/dns-debugging-resolution/).
