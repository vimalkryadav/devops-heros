#!/usr/bin/env python3
"""Verify observed monitoring data, alerts and GitOps behavior on the lab cluster."""
import argparse
from datetime import datetime, timezone
import json
from pathlib import Path
import shlex
import subprocess
import threading
import time
import urllib.error
import urllib.parse
import urllib.request

parser = argparse.ArgumentParser()
parser.add_argument('phase', choices=['monitor', 'gitops', 'drift'])
parser.add_argument('--revision')
args = parser.parse_args()
root = Path(__file__).resolve().parent.parent
evidence = root / 'evidence'
evidence.mkdir(exist_ok=True)
namespace = 'assignment-s20'
ports = []
stop = threading.Event()

def save(name, data):
    (evidence / name).write_text(json.dumps(data, indent=2) + '\n')

def command(*words):
    print('$ ' + shlex.join(words), flush=True)
    result = subprocess.run(words, capture_output=True, text=True, check=True)
    print(result.stdout, end='', flush=True)
    return result.stdout

def request(port, path, body=None):
    encoded = None if body is None else json.dumps(body).encode()
    req = urllib.request.Request(f'http://127.0.0.1:{port}{path}', data=encoded,
                                 headers={'Content-Type': 'application/json'})
    try:
        with urllib.request.urlopen(req, timeout=10) as response:
            text = response.read().decode()
    except urllib.error.HTTPError as error:
        if error.code != 503:
            raise
        text = error.read().decode()
    try:
        return json.loads(text)
    except json.JSONDecodeError:
        return text

def wait(description, predicate, seconds=180):
    deadline = time.monotonic() + seconds
    while True:
        try:
            result = predicate()
            if result:
                print('PASS: ' + description, flush=True)
                return result
        except (OSError, KeyError, ValueError):
            pass
        if time.monotonic() > deadline:
            raise TimeoutError(description)
        time.sleep(3)

def forward(service, local, remote, health):
    stream = (evidence / f'port-forward-{service}.txt').open('a')
    proc = subprocess.Popen(['kubectl', '-n', namespace, 'port-forward',
                             f'service/{service}', f'{local}:{remote}', '--address=127.0.0.1'],
                            stdout=stream, stderr=subprocess.STDOUT)
    ports.append((proc, stream))
    wait(service + ' forwarding is available', lambda: request(local, health))

def query(expression):
    return request(19090, '/api/v1/query?' + urllib.parse.urlencode({'query': expression}))

def application():
    return json.loads(subprocess.check_output(['kubectl', '-n', 'argocd', 'get',
                                              'application', 'session20', '-o', 'json'], text=True))

def alert_state(expected):
    data = request(19090, '/api/v1/alerts')
    matching = [alert for alert in data['data']['alerts']
                if alert['labels']['alertname'] == 'ApplicationErrors']
    matches = any(alert['state'] == 'firing' for alert in matching) if expected == 'firing' else not matching
    return data if matches else None

def traffic():
    while not stop.is_set():
        try:
            request(18020, '/work')
        except OSError:
            pass
        stop.wait(0.2)

print('Verification started:', datetime.now(timezone.utc).isoformat(), flush=True)
try:
    command('kubectl', '-n', namespace, 'rollout', 'status', 'deployment/release-monitor', '--timeout=300s')
    forward('release-monitor', 18020, 8000, '/healthz')
    if args.phase == 'monitor':
        for service in ['prometheus', 'grafana']:
            command('kubectl', '-n', namespace, 'rollout', 'status', f'deployment/{service}', '--timeout=300s')
        forward('prometheus', 19090, 9090, '/-/ready')
        forward('grafana', 13000, 3000, '/api/health')
        threading.Thread(target=traffic, daemon=True).start()
        wait('Prometheus scrapes the application as UP', lambda: any(
            item['value'][1] == '1' for item in query('up{job="release-monitor"}')['data']['result']))
        save('prometheus-targets.json', request(19090, '/api/v1/targets'))
        wait('Application CPU and request counters have rate samples', lambda: any(
            float(item['value'][1]) > 0 for item in query('rate(lab_process_cpu_seconds_total[1m])')['data']['result']))
        for _ in range(15):
            result = request(18020, '/fail')
            assert result['status'] == 503
            time.sleep(1)
        firing = wait('ApplicationErrors enters firing state', lambda: alert_state('firing'))
        save('alerts-firing.json', firing)
        print(json.dumps(firing, indent=2), flush=True)
        resolved = wait('ApplicationErrors resolves after successful traffic', lambda: alert_state('resolved'), 150)
        save('alerts-resolved.json', resolved)
        dashboard = request(13000, '/api/dashboards/uid/session20')
        save('grafana-dashboard.json', dashboard)
        results = {}
        for panel in dashboard['dashboard']['panels']:
            expression = panel['targets'][0]['expr']
            response = request(13000, '/api/ds/query', {
                'from': str(int((time.time() - 180) * 1000)), 'to': str(int(time.time() * 1000)),
                'queries': [{'refId': 'A', 'datasource': {'type': 'prometheus', 'uid': 'prometheus'},
                             'expr': expression, 'range': True, 'intervalMs': 5000, 'maxDataPoints': 100}]})
            frames = response['results']['A'].get('frames', [])
            values = [value for frame in frames for column in frame.get('data', {}).get('values', [])[1:]
                      for value in column if isinstance(value, (int, float))]
            assert values and max(values) > 0, (panel['title'], response)
            results[panel['title']] = {'expression': expression, 'samples': len(values),
                                      'minimum': min(values), 'maximum': max(values), 'response': response}
            print(panel['title'], 'samples:', len(values), 'max:', max(values), flush=True)
        save('grafana-panel-results.json', results)
        (evidence / 'metrics.txt').write_text(request(18020, '/metrics'))
        (evidence / 'pod-usage.txt').write_text(command('kubectl', '-n', namespace, 'top', 'pods'))
        (evidence / 'application-logs.txt').write_text(command('kubectl', '-n', namespace, 'logs',
                                                            'deployment/release-monitor', '--tail=30'))
    elif args.phase == 'gitops':
        assert args.revision, '--revision must identify the actual pushed commit'
        observed = wait('Argo CD syncs the pushed commit and is Healthy', lambda: (
            app if (app := application()).get('status', {}).get('sync', {}).get('revision') == args.revision
            and app['status']['sync']['status'] == 'Synced'
            and app['status']['health']['status'] == 'Healthy' else None), 240)
        response = wait('Application serves the Git-managed v2 configuration', lambda: (
            body if (body := request(18020, '/'))['version'] == 'v2' else None), 180)
        save('gitops-synced.json', observed)
        save('gitops-http.json', response)
        print(json.dumps(response, indent=2), flush=True)
    else:
        command('kubectl', '-n', namespace, 'scale', 'deployment/release-monitor', '--replicas=3')
        changed = json.loads(command('kubectl', '-n', namespace, 'get', 'deployment/release-monitor', '-o', 'json'))
        assert changed['spec']['replicas'] == 3
        save('drift-before.json', changed)
        restored = wait('Argo CD restores the Git-declared replica count of one', lambda: (
            obj if (obj := json.loads(subprocess.check_output(['kubectl', '-n', namespace, 'get',
                'deployment/release-monitor', '-o', 'json'], text=True)))['spec']['replicas'] == 1 else None))
        command('kubectl', '-n', namespace, 'rollout', 'status', 'deployment/release-monitor', '--timeout=120s')
        save('drift-restored.json', restored)
        save('drift-application.json', application())
    (evidence / f'workloads-{args.phase}.txt').write_text(command('kubectl', '-n', namespace, 'get',
                                                               'pods,deployments,services', '-o', 'wide'))
finally:
    stop.set()
    for process, stream in ports:
        process.terminate()
        try:
            process.wait(timeout=5)
        except subprocess.TimeoutExpired:
            process.kill()
            process.wait()
        stream.close()
