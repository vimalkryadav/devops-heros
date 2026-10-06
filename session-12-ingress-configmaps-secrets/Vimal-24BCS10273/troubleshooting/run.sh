#!/usr/bin/env bash
set -euo pipefail
cd -- "$(dirname -- "${BASH_SOURCE[0]}")"
mkdir -p evidence
exec > >(tee evidence/secret-fix.txt) 2>&1
run() { printf '\n$'; printf ' %q' "$@"; printf '\n'; "$@"; }
k() { kubectl -n assignment-s12 "$@"; }
check_password() { k exec password-client -- psql -h password-db -U assignment_user -d assignment -c 'SELECT current_user, current_database();'; }
check_length() { k exec password-client -- sh -c 'printf %s "$PGPASSWORD" | wc -c'; }
run date -u +'%Y-%m-%dT%H:%M:%SZ'
run kubectl config current-context
run kubectl create namespace assignment-s12
run k apply -f database.yaml -f broken-secret.yaml -f client.yaml
run k wait --for=condition=Ready pod/password-db pod/password-client --timeout=240s
run k get pods,service
run check_length
if run check_password; then echo 'ERROR: broken password succeeded'; exit 1; fi
run k logs password-db --tail=8
run k apply -f fixed-secret.yaml
printf '\nSecret fixed, but the existing environment variable is still stale:\n'
run check_length
if run check_password; then echo 'ERROR: environment changed without Pod replacement'; exit 1; fi
run k delete pod password-client --wait=true
run k apply -f client.yaml
run k wait --for=condition=Ready pod/password-client --timeout=120s
run check_length
run check_password
printf '\nAuthentication passed after correction and Pod replacement. Cleanup: kubectl delete namespace assignment-s12\n'
