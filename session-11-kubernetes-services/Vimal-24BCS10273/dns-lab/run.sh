#!/usr/bin/env bash
set -euo pipefail
cd -- "$(dirname -- "${BASH_SOURCE[0]}")"
mkdir -p evidence
exec > >(tee evidence/dns.txt) 2>&1
run() { printf '\n$'; printf ' %q' "$@"; printf '\n'; "$@"; }
run date -u +'%Y-%m-%dT%H:%M:%SZ'
run kubectl config current-context
run kubectl create namespace assignment-s11
run kubectl create namespace assignment-s11-client
run kubectl -n assignment-s11 apply -f catalog.yaml -f client.yaml
run kubectl -n assignment-s11-client apply -f client.yaml
run kubectl -n assignment-s11 rollout status deployment/catalog --timeout=180s
run kubectl -n assignment-s11 wait --for=condition=Ready pod/dns-client --timeout=180s
run kubectl -n assignment-s11-client wait --for=condition=Ready pod/dns-client --timeout=180s
run kubectl -n assignment-s11 exec dns-client -- cat /etc/resolv.conf
run kubectl -n assignment-s11 exec dns-client -- nslookup catalog.assignment-s11.svc.cluster.local.
run kubectl -n assignment-s11 exec dns-client -- wget -qO- http://catalog
if run kubectl -n assignment-s11-client exec dns-client -- wget -T 5 -qO- http://catalog; then
  echo 'ERROR: short name unexpectedly resolved from the other namespace'; exit 1
else
  echo 'Expected: no catalog Service in assignment-s11-client.'
fi
run kubectl -n assignment-s11-client exec dns-client -- wget -qO- http://catalog.assignment-s11
run kubectl -n assignment-s11-client exec dns-client -- nslookup catalog.assignment-s11.svc.cluster.local.
run kubectl -n assignment-s11-client exec dns-client -- wget -qO- http://catalog.assignment-s11.svc.cluster.local.
run kubectl -n assignment-s11 get service catalog -o wide
run kubectl -n assignment-s11 get endpointslices -l kubernetes.io/service-name=catalog
run kubectl -n kube-system get configmap coredns -o jsonpath='{.data.Corefile}'
run kubectl -n kube-system get deployment coredns
run kubectl -n kube-system get pods -l k8s-app=kube-dns -o wide
run kubectl -n kube-system get service kube-dns
run kubectl -n kube-system get endpointslices -l kubernetes.io/service-name=kube-dns
run kubectl -n kube-system logs deployment/coredns --tail=30
printf '\nDNS checks passed. Cleanup: kubectl delete namespace assignment-s11 assignment-s11-client\n'
