"""Small command recorder used by this assignment's reproducible lab."""
import contextlib
import datetime
import json
from pathlib import Path
import shlex
import subprocess
import time

ROOT = Path(__file__).resolve().parent
NS = 'assignment-s15'
_log = None

def note(text):
    print(text, flush=True)
    if _log:
        _log.write(text + '\n')
        _log.flush()

@contextlib.contextmanager
def record(name):
    global _log
    directory = ROOT / 'evidence'
    directory.mkdir(exist_ok=True)
    with (directory / (name + '.txt')).open('w') as stream:
        _log = stream
        note(datetime.datetime.now(datetime.timezone.utc).isoformat())
        try:
            yield
        finally:
            _log = None

def run(*args, expect=0, quiet=False, timeout=240):
    command = [str(arg) for arg in args]
    if not quiet: note('$ ' + shlex.join(command))
    result = subprocess.run(command, cwd=ROOT, text=True, stdout=subprocess.PIPE,
                            stderr=subprocess.STDOUT, timeout=timeout)
    if not quiet: note(result.stdout.rstrip())
    if expect is not None and result.returncode != expect:
        if quiet: note(result.stdout.rstrip())
        raise RuntimeError(f'{command!r}: exit {result.returncode}, expected {expect}')
    return result

def k(*args, **kwargs):
    return run('kubectl', '-n', NS, *args, **kwargs)

def data(*args):
    return json.loads(k('get', *args, '-o', 'json', quiet=True).stdout)

def poll(description, predicate, timeout=180, interval=3):
    note('Waiting: ' + description)
    started = time.monotonic()
    while time.monotonic() - started < timeout:
        result = predicate()
        if result:
            note(f'PASS: {description} ({time.monotonic()-started:.1f}s)')
            return result
        time.sleep(interval)
    raise TimeoutError(description)

def ready(pod):
    return any(c['type'] == 'Ready' and c['status'] == 'True'
               for c in pod.get('status',{}).get('conditions',[]))
