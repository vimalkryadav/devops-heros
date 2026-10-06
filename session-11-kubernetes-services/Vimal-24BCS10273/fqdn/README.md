# Fully qualified domain names

An FQDN identifies a name relative to the DNS root, instead of relying on a client's
search suffix. The usual Service name is:

```text
<service>.<namespace>.svc.<cluster-domain>.
catalog.assignment-s11.svc.cluster.local.
```

The final dot marks an absolute DNS name. `cluster.local` is this lab's configured
cluster domain, not a universal constant. A normal Service resolves to its
ClusterIP; a headless Service resolves to endpoint addresses. An ExternalName
Service supplies a CNAME to its configured external hostname and does not proxy
the connection.

| Client location | Name to use | What it means |
| --- | --- | --- |
| `assignment-s11` | `catalog` | Search for the Service in the client's namespace |
| `assignment-s11-client` | `catalog.assignment-s11` | Explicit namespace; the search list supplies the Service domain |
| Any namespace | `catalog.assignment-s11.svc.cluster.local.` | Absolute name in this cluster |
| `assignment-s11-client` | `catalog` | Searches the client namespace, where this lab has no such Service |

The kubelet writes `/etc/resolv.conf` for `dnsPolicy: ClusterFirst` Pods. Its
nameserver is the cluster DNS Service, and its search list starts with the Pod's
namespace. `ndots:5` affects which queries a resolver tries before the absolute
name. Inspect the actual file instead of assuming the host's DNS configuration.

For a StatefulSet with a governing headless Service, a Pod name can be
`db-0.database.assignment-s11.svc.cluster.local.`. A bare Pod does not automatically
receive that StatefulSet identity; hostname/subdomain and the corresponding
headless Service must be configured.

Run [the DNS lab](../dns-lab/run.sh) from a disposable local cluster. It checks
same-namespace access, the expected failure of a short name from another namespace,
and successful cross-namespace lookup and HTTP access. See the
[recorded output](../dns-lab/evidence/dns.txt) and [CoreDNS notes](../coredns/README.md).

In this BusyBox build, `nslookup` on a short name printed one successful answer
alongside failed search-suffix queries and returned a nonzero exit status. The lab
uses absolute names for `nslookup` and actual HTTP requests to verify short-name
resolution through the application's resolver. A tool's aggregate exit code
should not be mistaken for proof that every DNS query failed.

Reference: [DNS for Services and Pods](https://kubernetes.io/docs/concepts/services-networking/dns-pod-service/).
