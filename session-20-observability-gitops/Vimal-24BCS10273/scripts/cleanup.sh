#!/usr/bin/env bash
set -euo pipefail
# Remove the application while its controller is still running so pruning finishes.
kubectl -n argocd delete application session20 --ignore-not-found --wait=true --timeout=180s
kubectl delete namespace assignment-s20 --ignore-not-found --wait=true
# This lab installs Argo CD into a dedicated cluster; do not use on a shared installation.
file=$(mktemp)
trap 'rm -f "$file"' EXIT
if [[ -n "${ARGOCD_MANIFEST:-}" ]]; then
  cp "$ARGOCD_MANIFEST" "$file"
else
  curl --max-time 180 --retry 2 -fsSL 'https://raw.githubusercontent.com/argoproj/argo-cd/c9c369efcc5b2a0bd720803f8d14a1c3eaddf579/manifests/core-install.yaml' -o "$file"
fi
printf '%s  %s\n' '1a87025d8eb2eae621653fd312fb9ca51df1b4b3b6992a030e3a9ef38e45c448' "$file" | sha256sum -c -
kubectl -n argocd delete -f "$file" --ignore-not-found --wait=true
kubectl delete namespace argocd --ignore-not-found --wait=true
kubectl get namespaces
