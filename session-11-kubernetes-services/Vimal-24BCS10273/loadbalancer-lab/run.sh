#!/usr/bin/env bash
set -euo pipefail
cd "$(dirname "$0")"
mkdir -p evidence
# This is a dedicated Linux Minikube Docker cluster, not a shared cluster.
# Confirm its Docker subnet and choose unused addresses before applying pool.yaml.
docker network inspect devops-assignment --format '{{json .IPAM.Config}} {{json .Containers}}'
helm repo add metallb https://metallb.github.io/metallb --force-update
helm upgrade --install assignment-metallb "${METALLB_CHART:-metallb/metallb}" \
  --version 0.16.1 --namespace metallb-system --create-namespace \
  --set frrk8s.enabled=false --set speaker.ignoreExcludeLB=true --wait --timeout 10m
cleanup() {
  kubectl delete namespace assignment-s11-lb --ignore-not-found --wait=true
  kubectl delete -f pool.yaml --ignore-not-found
  helm uninstall assignment-metallb --namespace metallb-system --wait
  kubectl delete namespace metallb-system --ignore-not-found --wait=true
}
trap cleanup EXIT
kubectl apply -f pool.yaml
kubectl apply -f workload.yaml
kubectl -n assignment-s11-lb rollout status deployment/campus-web --timeout=180s
kubectl -n assignment-s11-lb wait service/campus-web-loadbalancer \
  --for=jsonpath='{.status.loadBalancer.ingress[0].ip}' --timeout=120s
kubectl -n assignment-s11-lb get pods,services -o wide | tee evidence/workloads.txt
kubectl -n assignment-s11-lb get service campus-web-loadbalancer -o json > evidence/service.json
kubectl -n metallb-system get ipaddresspool,l2advertisement -o yaml > evidence/pool.yaml
address=$(kubectl -n assignment-s11-lb get service campus-web-loadbalancer -o jsonpath='{.status.loadBalancer.ingress[0].ip}')
printf 'Requesting the assigned external IP: http://%s:80\n' "$address"
curl --fail --show-error --silent --retry 8 --retry-delay 2 --retry-all-errors --max-time 10 \
  --dump-header evidence/http-headers.txt "http://$address:80" | tee evidence/http-body.html
cat evidence/http-headers.txt
grep -q 'Welcome to nginx!' evidence/http-body.html
kubectl -n metallb-system logs deployment/assignment-metallb-controller --tail=30 > evidence/controller.txt
printf 'PASS: HTTP 200 through the assigned external LoadBalancer IP\n'
