#!/usr/bin/env bash
set -euo pipefail
cd -- "$(dirname -- "${BASH_SOURCE[0]}")"
namespace=assignment-s09
mkdir -p evidence
exec > >(tee evidence/tutorial.txt) 2>&1

run() { printf '\n$'; printf ' %q' "$@"; printf '\n'; "$@"; }
k() { kubectl -n "$namespace" "$@"; }

run date -u +'%Y-%m-%dT%H:%M:%SZ'
run kubectl config current-context
run kubectl version
run kubectl cluster-info
run kubectl get nodes -o wide
run kubectl get pods -n kube-system -o wide
run kubectl create namespace "$namespace"
run k apply --dry-run=server -f deployment.yaml -f service.yaml
run k apply -f deployment.yaml
run k rollout status deployment/kubernetes-bootcamp --timeout=180s
run k get deployment,replicaset,pods -o wide
pod=$(k get pods -l app=kubernetes-bootcamp -o jsonpath='{.items[0].metadata.name}')
run k describe pod "$pod"
run k logs "$pod"
run k exec "$pod" -- env
run k apply -f service.yaml
run k get service kubernetes-bootcamp
run k get endpointslices -l kubernetes.io/service-name=kubernetes-bootcamp

# Minikube's Docker driver exposes NodePort directly on Linux.
node_ip=$(minikube -p devops-assignment ip)
node_port=$(k get service kubernetes-bootcamp -o jsonpath='{.spec.ports[0].nodePort}')
run curl --fail --silent --show-error --retry 5 --retry-connrefused --retry-delay 1 --max-time 10 "http://$node_ip:$node_port"
run k scale deployment kubernetes-bootcamp --replicas=4
run k rollout status deployment/kubernetes-bootcamp --timeout=180s
run k get pods -l app=kubernetes-bootcamp -o wide
run k get endpointslices -l kubernetes.io/service-name=kubernetes-bootcamp
run k scale deployment kubernetes-bootcamp --replicas=2
run k rollout status deployment/kubernetes-bootcamp --timeout=180s
run k set image deployment/kubernetes-bootcamp kubernetes-bootcamp=docker.io/jocatalin/kubernetes-bootcamp:v2
run k rollout status deployment/kubernetes-bootcamp --timeout=180s
run k get replicasets,pods -l app=kubernetes-bootcamp -o wide
run curl --fail --silent --show-error --retry 5 --retry-connrefused --retry-delay 1 --max-time 10 "http://$node_ip:$node_port"
run k rollout history deployment/kubernetes-bootcamp
run k set image deployment/kubernetes-bootcamp kubernetes-bootcamp=gcr.io/google-samples/kubernetes-bootcamp:v10
if run k rollout status deployment/kubernetes-bootcamp --timeout=45s; then
  echo 'ERROR: the deliberately missing v10 image unexpectedly rolled out'; exit 1
fi
run k get pods -l app=kubernetes-bootcamp
run k describe pods -l app=kubernetes-bootcamp
run k rollout undo deployment/kubernetes-bootcamp
run k rollout status deployment/kubernetes-bootcamp --timeout=180s
run curl --fail --silent --show-error --retry 5 --retry-connrefused --retry-delay 1 --max-time 10 "http://$node_ip:$node_port"
run k get deployment kubernetes-bootcamp -o wide
printf '\nAll six tutorial modules completed. Cleanup: kubectl delete namespace %s\n' "$namespace"
