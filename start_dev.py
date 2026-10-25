#!/usr/bin/env python3
"""
start_dev.py — One-command local dev startup for Windows/Mac/Linux.

Starts both the FastAPI backend and the Vite frontend simultaneously.
Press Ctrl+C to stop both.

Usage:
    python start_dev.py
"""
import subprocess
import sys
import os
import signal
import time
from pathlib import Path

ROOT = Path(__file__).parent
FRONTEND_DIR = ROOT / "frontend"

# On Windows, npm/npx are .cmd files and need shell=True or full path
IS_WINDOWS = sys.platform == "win32"

BACKEND_CMD = [sys.executable, "-m", "uvicorn", "backend.app.main:app",
               "--reload", "--host", "127.0.0.1", "--port", "8000"]

# Use shell=True on Windows so PATH is fully resolved (finds npm.cmd etc.)
FRONTEND_CMD = "npm run dev"

processes = []


def shutdown(sig=None, frame=None):
    print("\n[dev] Shutting down both servers...")
    for p in processes:
        try:
            p.terminate()
        except Exception:
            pass
    sys.exit(0)


signal.signal(signal.SIGINT, shutdown)
if hasattr(signal, "SIGTERM"):
    signal.signal(signal.SIGTERM, shutdown)


def check_env():
    env_file = ROOT / ".env"
    if not env_file.exists():
        print("[dev] WARNING: .env file not found. Copy .env.example to .env and fill in credentials.")
        return
    content = env_file.read_text()
    if "your_gemini_api_key_here" in content:
        print("[dev] NOTE: GEMINI_API_KEY not set in .env -- AI summaries skipped (non-critical).")
    for line in content.splitlines():
        if line.startswith("DATABASE_URL="):
            val = line.split("=", 1)[1].strip()
            if val.startswith("sqlite"):
                print("[dev] Using SQLite (local). To use Neon DB, update DATABASE_URL in .env.")
            elif "neon.tech" in val:
                print("[dev] Using Neon PostgreSQL.")
            break


def install_frontend_deps():
    node_modules = FRONTEND_DIR / "node_modules"
    if not node_modules.exists():
        print("[dev] Installing frontend dependencies (npm install)...")
        subprocess.run("npm install", cwd=FRONTEND_DIR, shell=True, check=True)
    else:
        print("[dev] Frontend node_modules already present — skipping npm install.")


if __name__ == "__main__":
    print("=" * 60)
    print("  Green Campus Sustainability Auditor — Dev Server")
    print("=" * 60)
    check_env()
    install_frontend_deps()

    print("\n[dev] Starting backend  -> http://127.0.0.1:8000")
    print("[dev] Starting frontend -> http://localhost:5173")
    print("[dev] API docs          -> http://127.0.0.1:8000/api/docs")
    print("[dev] Press Ctrl+C to stop both.\n")

    # Start backend
    backend = subprocess.Popen(BACKEND_CMD, cwd=ROOT)
    processes.append(backend)

    time.sleep(2)  # Give backend a moment to start

    # Start frontend — always shell=True to resolve npm.cmd on Windows
    frontend = subprocess.Popen(FRONTEND_CMD, cwd=FRONTEND_DIR, shell=True)
    processes.append(frontend)

    # Keep running until Ctrl+C or a process dies
    while True:
        for p in processes:
            ret = p.poll()
            if ret is not None:
                print(f"[dev] A process exited (code {ret}). Shutting down...")
                shutdown()
        time.sleep(1)
