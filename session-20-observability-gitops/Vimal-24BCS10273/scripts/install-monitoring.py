#!/usr/bin/env python3
"""Install the local monitoring demo without putting a password in a file or log."""
import json
from pathlib import Path
import secrets
import subprocess

root = Path(__file__).resolve().parent.parent
subprocess.run(['kubectl', 'apply', '-f', str(root / 'namespace.yaml')], check=True)
existing = subprocess.run(['kubectl', '-n', 'assignment-s20', 'get', 'secret',
                           'grafana-admin', '--ignore-not-found', '-o', 'name'],
                          capture_output=True, text=True, check=True)
if not existing.stdout.strip():
    secret = {'apiVersion': 'v1', 'kind': 'Secret', 'metadata': {
        'name': 'grafana-admin', 'namespace': 'assignment-s20'},
        'type': 'Opaque', 'stringData': {'password': secrets.token_urlsafe(32)}}
    subprocess.run(['kubectl', 'create', '-f', '-'], input=json.dumps(secret), text=True, check=True)
for name in ['prometheus.yaml', 'grafana.yaml']:
    subprocess.run(['kubectl', 'apply', '-f', str(root / 'monitoring' / name)], check=True)
subprocess.run(['kubectl', 'apply', '-f', str(root / 'gitops/argocd-application.yaml')], check=True)
