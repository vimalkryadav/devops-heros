#!/usr/bin/env python3
"""Run the twelve classroom cases and save observed output for each one."""
import argparse
import datetime
import json
from pathlib import Path
import shlex
import subprocess
import time

ROOT = Path(__file__).resolve().parent
EVIDENCE = ROOT / "evidence"
EVIDENCE.mkdir(exist_ok=True)
NAMESPACE = "assignment-s10-lifecycle"
K = ["kubectl", "-n", NAMESPACE]
parser = argparse.ArgumentParser(description=__doc__)
parser.add_argument("--start-case", type=int, choices=range(1, 13), default=1)
args = parser.parse_args()
if args.start_case == 1:
    subprocess.run(["kubectl", "create", "namespace", NAMESPACE], check=True)

def record(output, *args, check=True):
    output.write("\n$ " + shlex.join(args) + "\n")
    output.flush()
    result = subprocess.run(args, stdout=subprocess.PIPE, stderr=subprocess.STDOUT, text=True)
    output.write(result.stdout)
    output.flush()
    if check and result.returncode:
        raise RuntimeError(result.stdout)
    return result

def status(name):
    return json.loads(subprocess.check_output(K + ["get", "pod", name, "-o", "json"]))["status"]

def wait_for(name, predicate, timeout=180):
    deadline = time.monotonic() + timeout
    while time.monotonic() < deadline:
        current = status(name)
        if predicate(current):
            return current
        time.sleep(2)
    raise TimeoutError(f"{name} did not reach the required state: {current}")

def containers(s):
    return s.get("containerStatuses", [])

def ready(s):
    return bool(containers(s)) and all(c.get("ready") for c in containers(s))

def waiting_reason(s):
    return containers(s)[0].get("state", {}).get("waiting", {}).get("reason") if containers(s) else None

for number, name in enumerate([
    "lc-running", "lc-pending", "lc-succeeded", "lc-failed", "lc-crashloop",
    "lc-image-error", "lc-readiness", "lc-liveness", "lc-startup", "lc-init",
    "lc-multi", "lc-termination",
], 1):
    if number < args.start_case:
        continue
    manifest = next((ROOT / "lifecycle").glob(f"{number:02}-*.yaml"))
    with (EVIDENCE / f"{number:02}-{name}.txt").open("w") as output:
        output.write(datetime.datetime.now(datetime.timezone.utc).isoformat() + "\n")
        record(output, "kubectl", "config", "current-context")
        # Absolute path keeps this runner usable from any working directory.
        record(output, *K, "apply", "-f", str(manifest))
        if number == 2:
            wait_for(name, lambda s: any(c.get("reason") == "Unschedulable" for c in s.get("conditions", [])))
        elif number in (3, 4):
            wait_for(name, lambda s: s.get("phase") == ("Succeeded" if number == 3 else "Failed"))
        elif number == 5:
            wait_for(name, lambda s: bool(containers(s)) and containers(s)[0].get("restartCount", 0) >= 2)
            result = record(output, *K, "get", "events", "--field-selector", f"involvedObject.name={name}", "--sort-by=.lastTimestamp")
            assert "BackOff" in result.stdout
        elif number == 6:
            wait_for(name, lambda s: waiting_reason(s) == "ImagePullBackOff")
        elif number == 7:
            wait_for(name, lambda s: s.get("phase") == "Running" and not ready(s))
            record(output, *K, "get", "pod", name)
            record(output, *K, "exec", name, "--", "touch", "/tmp/ready")
            wait_for(name, ready)
        elif number == 8:
            wait_for(name, ready)
            record(output, *K, "exec", name, "--", "rm", "/tmp/healthy")
            wait_for(name, lambda s: ready(s) and containers(s)[0].get("restartCount", 0) >= 1)
        elif number == 9:
            wait_for(name, lambda s: s.get("phase") == "Running" and not ready(s))
            record(output, *K, "get", "pod", name)
            record(output, *K, "logs", name)
            final = wait_for(name, ready)
            assert containers(final)[0]["restartCount"] == 0
        elif number == 10:
            wait_for(name, lambda s: bool(s.get("initContainerStatuses")))
            record(output, *K, "get", "pod", name)
            wait_for(name, ready)
            record(output, *K, "logs", name, "-c", "seed")
            record(output, *K, "logs", name, "-c", "app")
        else:
            wait_for(name, ready)
        record(output, *K, "get", "pod", name, "-o", "wide")
        record(output, *K, "get", "pod", name, "-o", 'jsonpath={.status.phase}{"\\n"}{.status.containerStatuses}{"\\n"}')
        record(output, *K, "describe", "pod", name)
        if number in (3, 4, 5, 8, 9):
            record(output, *K, "logs", name)
        if number == 11:
            record(output, *K, "logs", name, "-c", "client")
            record(output, *K, "exec", name, "-c", "client", "--", "wget", "-qO-", "http://127.0.0.1:8080")
        if number == 12:
            output.write("\n$ kubectl logs -f lc-termination (captured during deletion)\n")
            follower = subprocess.Popen(K + ["logs", "-f", name], stdout=subprocess.PIPE, stderr=subprocess.STDOUT, text=True)
            time.sleep(1)
            record(output, *K, "delete", "pod", name, "--wait=true", "--timeout=45s")
            log, _ = follower.communicate(timeout=15)
            output.write(log)
            assert "SIGTERM-received" in log and "cleanup-complete" in log
    print(f"PASS {number:02}: {name}", flush=True)

print("All twelve cases observed. Cleanup: kubectl delete namespace " + NAMESPACE)
