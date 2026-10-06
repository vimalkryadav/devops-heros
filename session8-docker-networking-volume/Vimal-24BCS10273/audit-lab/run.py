#!/usr/bin/env python3
"""Repeat the networking, native host networking and bind-mount exercises."""
from datetime import datetime, timezone
import json
from pathlib import Path
import secrets
import shlex
import socket
import subprocess
import tempfile
import time
import urllib.request

root = Path(__file__).resolve().parent
evidence = root / 'evidence'
evidence.mkdir(exist_ok=True)
prefix = 'devops-s08-'
networks, containers = [], []
images = {
    'backend': 'alpine:3.24@sha256:294b683cb724975bec92580e1e685676bd4b50bda910ddb8c51d4cabeaec77e6',
    'frontend': 'nginx:stable-alpine@sha256:0985e772fb9f729e6fa0980da05fca5d9c468e870eed43071545afa9d2e27d94',
    'database': 'mysql:8.4@sha256:6ea90827b1100f8f2ae306a539f86d2c264a26ed435a2a9f75551dd5c3aeb242',
    'apache': 'httpd:2.4-alpine@sha256:3440c39d8d6f54fa9ad2549e5a60c19ddd435faadc29c1ad28aa795f71888889',
}

def run(*args, allowed=(0,)):
    print('$ ' + shlex.join(args), flush=True)
    result = subprocess.run(args, capture_output=True, text=True)
    print(result.stdout, end='', flush=True)
    print(result.stderr, end='', flush=True)
    if result.returncode not in allowed:
        raise RuntimeError(f'Command exited {result.returncode}')
    return result

def inspect(name):
    return json.loads(run('docker', 'inspect', prefix + name).stdout)[0]

def http(port):
    for attempt in range(60):
        try:
            with urllib.request.urlopen(f'http://127.0.0.1:{port}', timeout=2) as response:
                return response.read().decode()
        except OSError:
            if attempt == 59:
                raise
            time.sleep(1)

def start(name, *args):
    run('docker', 'run', '-d', '--name', prefix + name, '--label', 'assignment.session=8', *args)
    containers.append(prefix + name)

print('Started:', datetime.now(timezone.utc).isoformat(), flush=True)
for name in ['frontend', 'backend', 'database', 'apache']:
    exists = subprocess.run(['docker', 'inspect', prefix + name], capture_output=True)
    if exists.returncode == 0:
        raise RuntimeError('Existing container would conflict: ' + prefix + name)
for name in ['frontend', 'backend', 'database']:
    exists = subprocess.run(['docker', 'network', 'inspect', prefix + name], capture_output=True)
    if exists.returncode == 0:
        raise RuntimeError('Existing network would conflict: ' + prefix + name)
for port in [80, 18088]:
    with socket.socket() as check:
        if check.connect_ex(('127.0.0.1', port)) == 0:
            raise RuntimeError(f'Port {port} is already in use')
try:
    for image in images.values():
        run('docker', 'pull', image)
    with tempfile.TemporaryDirectory(prefix='devops-s08-') as directory:
        temporary = Path(directory)
        password = temporary / 'mysql-password'
        password.write_text(secrets.token_urlsafe(32))
        password.chmod(0o600)
        website = temporary / 'website'
        website.mkdir()
        index = website / 'index.html'
        index.write_text('Hello students\n')
        for name in ['frontend', 'backend', 'database']:
            network = prefix + name
            run('docker', 'network', 'create', '--label', 'assignment.session=8', network)
            networks.append(network)
        start('frontend', '--network', prefix + 'frontend', '-p', '127.0.0.1:18088:80',
              '--mount', f'type=bind,src={website},dst=/usr/share/nginx/html,readonly', images['frontend'])
        run('docker', 'network', 'connect', prefix + 'backend', prefix + 'frontend')
        start('backend', '--network', prefix + 'backend', images['backend'], 'sleep', 'infinity')
        run('docker', 'network', 'connect', prefix + 'database', prefix + 'backend')
        start('database', '--network', prefix + 'database', '-e',
              'MYSQL_ROOT_PASSWORD_FILE=/run/secrets/mysql-password', '--mount',
              f'type=bind,src={password},dst=/run/secrets/mysql-password,readonly', images['database'])
        membership = {}
        for name in ['frontend', 'backend', 'database']:
            output = run('docker', 'inspect', '--format', '{{json .NetworkSettings.Networks}}', prefix + name)
            membership[name] = list(json.loads(output.stdout))
        assert len(membership['backend']) == 2
        assert set(membership['backend']) == {prefix + 'backend', prefix + 'database'}
        assert not set(membership['frontend']) & set(membership['database'])
        run('docker', 'exec', prefix + 'backend', 'ping', '-c', '3', prefix + 'frontend')
        run('docker', 'exec', prefix + 'backend', 'ping', '-c', '3', prefix + 'database')
        isolated = run('docker', 'exec', prefix + 'frontend', 'getent', 'hosts', prefix + 'database', allowed=(0, 2))
        assert isolated.returncode == 2 and not isolated.stdout.strip()
        print('PASS: backend has exactly two networks; frontend cannot resolve database', flush=True)
        (evidence / 'networks.json').write_text(json.dumps(membership, indent=2) + '\n')
        before = run('docker', 'inspect', '--format', '{{.Id}} {{.State.StartedAt}}', prefix + 'frontend').stdout.strip()
        body_before = http(18088)
        assert body_before == 'Hello students\n'
        run('curl', '--fail', '--silent', '--show-error', 'http://127.0.0.1:18088')
        index.write_text('Hello students — bind mount updated\n')
        body_after = http(18088)
        assert body_after == 'Hello students — bind mount updated\n'
        run('curl', '--fail', '--silent', '--show-error', 'http://127.0.0.1:18088')
        after = run('docker', 'inspect', '--format', '{{.Id}} {{.State.StartedAt}}', prefix + 'frontend').stdout.strip()
        assert before == after
        (evidence / 'bind-mount.json').write_text(json.dumps({'before': body_before, 'after': body_after,
            'container_before': before, 'container_after': after, 'restarted': False}, indent=2) + '\n')
        print('PASS: bind-mounted content changed with identical container ID and start time', flush=True)
        start('apache', '--network', 'host', images['apache'], 'sh', '-c',
              "sed -i 's/^Listen 80$/Listen 127.0.0.1:80/' /usr/local/apache2/conf/httpd.conf; exec httpd-foreground")
        apache = http(80)
        assert 'It works!' in apache
        run('docker', 'inspect', '--format', 'NetworkMode={{.HostConfig.NetworkMode}} Ports={{json .HostConfig.PortBindings}}', prefix + 'apache')
        run('curl', '--fail', '--silent', '--show-error', 'http://localhost:80')
        print('PASS: host terminal reaches Apache directly on localhost:80', flush=True)
        run('docker', 'ps', '--filter', 'label=assignment.session=8', '--format', 'table {{.Names}}\t{{.Status}}\t{{.Ports}}')
        (evidence / 'host-network.json').write_text(json.dumps({'network_mode': 'host', 'port': 80,
            'response': apache, 'client': 'native Linux host curl'}, indent=2) + '\n')
finally:
    for name in reversed(containers):
        run('docker', 'rm', '-fv', name)
    for name in reversed(networks):
        run('docker', 'network', 'rm', name)
    remaining = run('docker', 'ps', '-a', '--filter', 'label=assignment.session=8', '--format', '{{.Names}}').stdout.strip()
    remaining_networks = run('docker', 'network', 'ls', '--filter', 'label=assignment.session=8', '--format', '{{.Name}}').stdout.strip()
    assert not remaining and not remaining_networks
    (evidence / 'cleanup.json').write_text(json.dumps({'containers': [], 'networks': [],
        'finished': datetime.now(timezone.utc).isoformat()}, indent=2) + '\n')
    print('PASS: all lab containers, MySQL anonymous volumes and networks removed', flush=True)
