#!/usr/bin/env python3
"""svc.py — reconcile services against env/services.yml (single source of truth).

Usage:
  svc.py status   print desired vs actual table, mark drift (read-only)
  svc.py sync     reconcile: start services desired=online but offline,
                  stop services desired=offline but online.

services.yml declares only `name` + `desired`. ALL lifecycle operations go
through the Makefile:
  make <name>.start   bring service online
  make <name>.stop    bring service offline
  make <name>.status  exit 0 = online, non-zero = offline
svc.py itself holds no start/stop/check commands.
"""
import subprocess
import sys
from pathlib import Path

import yaml

WS = Path(__file__).resolve().parent.parent
SVC_FILE = WS / "env" / "services.yml"
STATUS_TIMEOUT = 180


def load_services():
    with open(SVC_FILE) as f:
        data = yaml.safe_load(f)
    svcs = data["services"]
    names = [s["name"] for s in svcs]
    if len(names) != len(set(names)):
        sys.exit(f"error: duplicate service names in {SVC_FILE}")
    return svcs


def actual_state(name):
    """'online' or 'offline', derived solely from `make -s <name>.status` exit code."""
    try:
        r = subprocess.run(["make", "-s", f"{name}.status"], cwd=WS,
                           stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL,
                           timeout=STATUS_TIMEOUT)
    except subprocess.TimeoutExpired:
        return "offline"
    return "online" if r.returncode == 0 else "offline"


def run_make(target):
    print(f"  $ make {target}")
    r = subprocess.run(["make", target], cwd=WS)
    if r.returncode != 0:
        print(f"  !! make {target} failed (exit {r.returncode})")
    return r.returncode


def gather():
    rows = []
    for svc in load_services():
        actual = actual_state(svc["name"])
        drift = actual != svc["desired"]
        rows.append((svc, actual, drift))
    return rows


def cmd_status():
    rows = gather()
    w = max(len(s["name"]) for s, _, _ in rows)
    print(f"{'SERVICE':<{w}}  {'DESIRED':<8} {'ACTUAL':<8} STATE")
    print(f"{'-'*w}  {'-'*8} {'-'*8} -----")
    n_drift = 0
    for svc, actual, drift in rows:
        if drift:
            n_drift += 1
            state = f"DRIFT (want {svc['desired']}, is {actual})"
        else:
            state = "ok"
        print(f"{svc['name']:<{w}}  {svc['desired']:<8} {actual:<8} {state}")
    print(f"\n{len(rows)} services, {n_drift} drift")
    return 0


def cmd_sync():
    rows = gather()
    drifts = [(svc, actual) for svc, actual, drift in rows if drift]
    if not drifts:
        print("no drift, nothing to do")
        return 0
    for svc, actual in drifts:
        print(f"[sync] {svc['name']}: desired={svc['desired']} actual={actual}")
        run_make(f"{svc['name']}.start" if svc["desired"] == "online"
                 else f"{svc['name']}.stop")
    # re-check
    print("\n--- after sync ---")
    return cmd_status()


def main():
    if len(sys.argv) != 2 or sys.argv[1] not in ("status", "sync"):
        sys.exit(__doc__)
    sys.exit(cmd_status() if sys.argv[1] == "status" else cmd_sync())


if __name__ == "__main__":
    main()
