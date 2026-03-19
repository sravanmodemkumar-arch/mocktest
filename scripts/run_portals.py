"""
Launch one Django portal instance per portal group on separate ports.

Usage:
    python scripts/run_portals.py

Portal groups and ports:
    Group 1  — Platform Admin    → http://localhost:8010
    Group 2  — Chain Admin       → http://localhost:8020
    Group 3  — School            → http://localhost:8030
    Group 4  — College           → http://localhost:8040
    Group 5  — Coaching          → http://localhost:8050
    Group 6  — Exam Domain       → http://localhost:8060
    Group 7  — TSP               → http://localhost:8070
    Group 9  — B2B Partner       → http://localhost:8090
    Group 10 — Student Unified   → http://localhost:8100

The dev API server must already be running on port 8001:
    python scripts/dev_server.py
"""

import os
import sys
import subprocess
import signal
import time

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
PORTAL_DIR = os.path.join(BASE_DIR, "portal")

# Detect venv python
if sys.platform == "win32":
    PYTHON = os.path.join(BASE_DIR, "venv", "Scripts", "python.exe")
else:
    PYTHON = os.path.join(BASE_DIR, "venv", "bin", "python")

if not os.path.exists(PYTHON):
    PYTHON = sys.executable

GROUPS = [
    (1, 8010, "Platform Admin"),
    (2, 8020, "Chain Admin"),
    (3, 8030, "School"),
    (4, 8040, "College"),
    (5, 8050, "Coaching"),
    (6, 8060, "Exam Domain"),
    (7, 8070, "TSP"),
    (9, 8090, "B2B Partner"),
    (10, 8100, "Student Unified"),
]

processes = []


def start_portals():
    print("Starting portal instances...\n")
    for group, port, label in GROUPS:
        env = os.environ.copy()
        env["DJANGO_SETTINGS_MODULE"] = "portal.settings"
        env["DEV_PORTAL_GROUP"] = str(group)

        proc = subprocess.Popen(
            [PYTHON, "manage.py", "runserver", f"127.0.0.1:{port}", "--noreload"],
            cwd=PORTAL_DIR,
            env=env,
            stdout=subprocess.DEVNULL,
            stderr=subprocess.DEVNULL,
        )
        processes.append(proc)
        print(f"  Group {group:>2}  {label:<20}  http://localhost:{port}")

    print(f"\nAll {len(GROUPS)} portals running.")
    print("Login with any test user (password: Test@1234)")
    print("\nPress Ctrl+C to stop all servers.\n")


def stop_portals():
    print("\nStopping all portal instances...")
    for proc in processes:
        try:
            proc.terminate()
        except Exception:
            pass
    time.sleep(1)
    for proc in processes:
        try:
            proc.kill()
        except Exception:
            pass
    print("Done.")


def main():
    start_portals()
    try:
        while True:
            time.sleep(1)
            # Check if any process died unexpectedly
            for i, proc in enumerate(processes):
                if proc.poll() is not None:
                    group, port, label = GROUPS[i]
                    print(
                        f"  [WARNING] Group {group} ({label}) on port {port} exited — restarting..."
                    )
                    env = os.environ.copy()
                    env["DJANGO_SETTINGS_MODULE"] = "portal.settings"
                    env["DEV_PORTAL_GROUP"] = str(group)
                    processes[i] = subprocess.Popen(
                        [
                            PYTHON,
                            "manage.py",
                            "runserver",
                            f"127.0.0.1:{port}",
                            "--noreload",
                        ],
                        cwd=PORTAL_DIR,
                        env=env,
                        stdout=subprocess.DEVNULL,
                        stderr=subprocess.DEVNULL,
                    )
    except KeyboardInterrupt:
        stop_portals()


if __name__ == "__main__":
    main()
