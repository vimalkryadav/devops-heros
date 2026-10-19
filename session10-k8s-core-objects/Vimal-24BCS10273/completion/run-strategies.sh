#!/usr/bin/env bash
set -euo pipefail
cd -- "$(dirname -- "${BASH_SOURCE[0]}")"
mkdir -p evidence
exec > >(tee evidence/strategies.txt) 2>&1
run() { printf '\n$'; printf ' %q' "$@"; printf '\n'; "$@"; }
k() { kubectl -n assignment-s10-strategies "$@"; }
run date -u +'%Y-%m-%dT%H:%M:%SZ'
run kubectl config current-context
run kubectl create namespace assignment-s10-strategies
run k apply -f strategies/workloads.yaml
for deployment in portal-blue portal-green portal-stable portal-canary; do
  run k rollout status "deployment/$deployment" --timeout=180s
done
run k wait --for=condition=Ready pod/traffic-client --timeout=180s
run k get deployments,pods,services -o wide
run k exec traffic-client -- wget -qO- http://portal-active
run k patch service portal-active --type=merge -p '{"spec":{"selector":{"app":"portal-switch","version":"green-v2"}}}'
# Wait for the EndpointSlice controller and kube-proxy to propagate the switch.
for attempt in {1..30}; do
  active=$(k exec traffic-client -- wget -qO- http://portal-active)
  [[ "$active" == green-v2 ]] && break
  sleep 1
done
[[ "$active" == green-v2 ]]
run k get endpointslices -l kubernetes.io/service-name=portal-active -o wide
run k exec traffic-client -- wget -qO- http://portal-active
run k patch service portal-active --type=merge -p '{"spec":{"selector":{"app":"portal-switch","version":"blue-v1"}}}'
for attempt in {1..30}; do
  active=$(k exec traffic-client -- wget -qO- http://portal-active)
  [[ "$active" == blue-v1 ]] && break
  sleep 1
done
[[ "$active" == blue-v1 ]]
run k exec traffic-client -- wget -qO- http://portal-active
run k get endpointslices -l kubernetes.io/service-name=portal-release -o wide
run k exec traffic-client -- sh -c 'for i in $(seq 1 100); do wget -qO- http://portal-release || exit 1; done > /tmp/responses; sort /tmp/responses | uniq -c; test "$(grep -c canary-v2 /tmp/responses)" -gt 0; test "$(grep -c stable-v1 /tmp/responses)" -gt 0'
printf '\nBoth versions received traffic. Four stable endpoints and one canary endpoint imply an approximate 20%% share, not an exact request quota.\n'
printf 'Cleanup: kubectl delete namespace assignment-s10-strategies\n'
