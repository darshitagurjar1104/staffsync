
"""
StaffSync — HR Management System
Master Python Orchestrator, CLI Controller, and Production Web Server
Zero external dependencies required (uses 100% Python Standard Library).
"""

import os
import sys
import time
import socket
import signal
import argparse
import threading
import subprocess
import webbrowser
from pathlib import Path
from http.server import SimpleHTTPRequestHandler
import socketserver
import urllib.request
import urllib.error

# Ensure UTF-8 output on Windows consoles
if hasattr(sys.stdout, "reconfigure"):
    try:
        sys.stdout.reconfigure(encoding="utf-8", errors="replace")
    except Exception:
        pass
if hasattr(sys.stderr, "reconfigure"):
    try:
        sys.stderr.reconfigure(encoding="utf-8", errors="replace")
    except Exception:
        pass

BASE_DIR = Path(__file__).resolve().parent
SERVER_DIR = BASE_DIR / "server"
CLIENT_DIR = BASE_DIR / "client"
DIST_DIR = CLIENT_DIR / "dist"
DATA_DB_DIR = BASE_DIR / "data" / "db"

MONGOD_PATHS = [
    r"C:\Program Files\MongoDB\Server\9.0\bin\mongod.exe",
    r"C:\Program Files\MongoDB\Server\8.0\bin\mongod.exe",
    r"C:\Program Files\MongoDB\Server\7.0\bin\mongod.exe",
    r"C:\Program Files\MongoDB\Server\6.0\bin\mongod.exe",
]

NODE_PATHS = [
    r"C:\Program Files\nodejs\node.exe",
    "node",
]

NPM_PATHS = [
    r"C:\Program Files\nodejs\npm.cmd",
    "npm.cmd",
    "npm",
]

def find_executable(candidates):
    for candidate in candidates:
        if os.path.isabs(candidate) and os.path.exists(candidate):
            return candidate
        from shutil import which
        w = which(candidate)
        if w:
            return w
    return None

def is_port_in_use(port, host="127.0.0.1"):
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        s.settimeout(0.6)
        try:
            s.connect((host, port))
            return True
        except (socket.timeout, ConnectionRefusedError, OSError):
            return False

def wait_for_port(port, timeout=20, host="127.0.0.1"):
    start = time.time()
    while time.time() - start < timeout:
        if is_port_in_use(port, host):
            return True
        time.sleep(0.5)
    return False

def banner():
    print("""
========================================================================
  [StaffSync] — Modern Human Resource Management System
  MERN Stack Application Manager & Python Orchestrator
========================================================================
  * MongoDB Port:  27017
  * Backend API:   http://127.0.0.1:5000
  * Frontend App:  http://localhost:5173
========================================================================
""")

def check_system():
    print("[System Diagnostic Check]")
    print(f" * Project Directory: {BASE_DIR}")
    
    # Check node
    node_exe = find_executable(NODE_PATHS)
    print(f" * Node.js Runtime:  {'[OK] Found (' + node_exe + ')' if node_exe else '[MISSING] Not Found'}")
    
    # Check npm
    npm_exe = find_executable(NPM_PATHS)
    print(f" * npm Package Tool: {'[OK] Found (' + npm_exe + ')' if npm_exe else '[MISSING] Not Found'}")

    # Check mongod
    mongod_exe = find_executable(MONGOD_PATHS)
    print(f" * MongoDB Server:   {'[OK] Found (' + mongod_exe + ')' if mongod_exe else '[INFO] In PATH or Service'}")

    # Check Ports
    mongo_active = is_port_in_use(27017)
    backend_active = is_port_in_use(5000)
    frontend_active = is_port_in_use(5173)

    print("\n[Active Port Status]")
    print(f" * MongoDB (27017):     {'[ACTIVE] Listening' if mongo_active else '[INACTIVE]'}")
    print(f" * Backend API (5000):   {'[ACTIVE] Listening' if backend_active else '[INACTIVE]'}")
    print(f" * Frontend UI (5173):   {'[ACTIVE] Listening' if frontend_active else '[INACTIVE]'}")

    if backend_active:
        try:
            req = urllib.request.Request("http://127.0.0.1:5000/api/health")
            with urllib.request.urlopen(req, timeout=2) as response:
                if response.status == 200:
                    print(" * Backend API Health:   [OK] Healthy (HTTP 200)")
        except Exception:
            pass

    print("========================================================================\n")

def ensure_mongodb():
    if is_port_in_use(27017):
        print("[MongoDB]: Already running on port 27017. [OK]")
        return None

    DATA_DB_DIR.mkdir(parents=True, exist_ok=True)
    mongod_exe = find_executable(MONGOD_PATHS)
    if not mongod_exe:
        print("[MongoDB Warning]: Could not find mongod.exe automatically.")
        return None

    print(f"[MongoDB]: Starting local MongoDB instance from {mongod_exe}...")
    cmd = [mongod_exe, "--dbpath", str(DATA_DB_DIR), "--port", "27017", "--bind_ip", "127.0.0.1"]
    proc = subprocess.Popen(cmd, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
    if wait_for_port(27017, timeout=15):
        print("[MongoDB]: Started and listening on port 27017. [OK]")
    else:
        print("[MongoDB]: Waiting for daemon initialization...")
    return proc

def run_seed():
    print("[Seed]: Initializing StaffSync database records...")
    node_exe = find_executable(NODE_PATHS)
    if not node_exe:
        print("[Error]: Node.js not detected.")
        return False

    seed_script = SERVER_DIR / "utils" / "seed.js"
    env = os.environ.copy()
    env["PATH"] = r"C:\Program Files\nodejs;" + env.get("PATH", "")
    res = subprocess.run([node_exe, str(seed_script)], cwd=str(SERVER_DIR), env=env)
    return res.returncode == 0

class SPAHandler(SimpleHTTPRequestHandler):
    """Serves the client/dist build directory with SPA routing and API proxying."""
    def __init__(self, *args, **kwargs):
        super().__init__(*args, directory=str(DIST_DIR), **kwargs)

    def do_GET(self):
        # Proxy /api requests to backend Node server
        if self.path.startswith("/api/"):
            target_url = f"http://127.0.0.1:5000{self.path}"
            try:
                req = urllib.request.Request(target_url, headers={k: v for k, v in self.headers.items() if k.lower() != 'host'})
                with urllib.request.urlopen(req) as resp:
                    self.send_response(resp.status)
                    for k, v in resp.getheaders():
                        self.send_header(k, v)
                    self.end_headers()
                    self.wfile.write(resp.read())
                return
            except urllib.error.HTTPError as e:
                self.send_response(e.code)
                for k, v in e.headers.items():
                    self.send_header(k, v)
                self.end_headers()
                self.wfile.write(e.read())
                return
            except Exception as e:
                self.send_response(502)
                self.end_headers()
                self.wfile.write(f'{{"error": "Backend API offline", "details": "{str(e)}"}}'.encode())
                return

        # Check if requested static file exists in dist
        file_path = DIST_DIR / self.path.lstrip("/")
        if not file_path.exists() and not self.path.startswith("/api"):
            self.path = "/index.html"

        return super().do_GET()

def serve_production(port=5173):
    if not (DIST_DIR / "index.html").exists():
        print("[Notice]: client/dist not built yet. Building production bundle now...")
        npm_exe = find_executable(NPM_PATHS)
        env = os.environ.copy()
        env["PATH"] = r"C:\Program Files\nodejs;" + env.get("PATH", "")
        subprocess.run([npm_exe, "run", "build"], cwd=str(CLIENT_DIR), env=env)

    print(f"\n[Python Web Server]: Serving StaffSync Production App on http://localhost:{port}")
    print("Press Ctrl+C to stop the server.\n")
    
    with socketserver.TCPServer(("", port), SPAHandler) as httpd:
        try:
            httpd.serve_forever()
        except KeyboardInterrupt:
            print("\n[Python Web Server]: Stopped.")

def start_full_application():
    banner()
    processes = []

    def signal_handler(sig, frame):
        print("\n\n[Shutting down StaffSync processes...]")
        for p in processes:
            try:
                p.terminate()
            except Exception:
                pass
        sys.exit(0)

    signal.signal(signal.SIGINT, signal_handler)

    # 1. Start MongoDB if needed
    mongo_proc = ensure_mongodb()
    if mongo_proc:
        processes.append(mongo_proc)

    node_exe = find_executable(NODE_PATHS)
    npm_exe = find_executable(NPM_PATHS)
    env = os.environ.copy()
    env["PATH"] = r"C:\Program Files\nodejs;" + env.get("PATH", "")

    # 2. Start Backend Server if not running
    if not is_port_in_use(5000):
        print("[Backend]: Starting StaffSync Node API server on port 5000...")
        backend_proc = subprocess.Popen(
            [node_exe, "server.js"],
            cwd=str(SERVER_DIR),
            env=env
        )
        processes.append(backend_proc)
        if wait_for_port(5000, timeout=12):
            print("[Backend]: API server online at http://127.0.0.1:5000. [OK]")
    else:
        print("[Backend]: API server already running on port 5000. [OK]")

    # 3. Start Frontend Client if not running
    if not is_port_in_use(5173):
        print("[Frontend]: Starting Vite dev server on http://localhost:5173...")
        frontend_proc = subprocess.Popen(
            [npm_exe, "run", "dev", "--", "--host", "0.0.0.0", "--port", "5173"],
            cwd=str(CLIENT_DIR),
            env=env
        )
        processes.append(frontend_proc)
        if wait_for_port(5173, timeout=15):
            print("[Frontend]: UI ready at http://localhost:5173. [OK]")
    else:
        print("[Frontend]: Frontend dev server already running on port 5173. [OK]")

    print("\n------------------------------------------------------------------------")
    print("[SUCCESS] StaffSync is running! Opening browser to http://localhost:5173 ...")
    print("------------------------------------------------------------------------")
    print("DEMO LOGIN CREDENTIALS:")
    print(" * HR Admin:   admin@staffsync.com         / admin123")
    print(" * Manager:    sarah.manager@staffsync.com / manager123")
    print(" * Employee:   alex.dev@staffsync.com      / employee123")
    print("------------------------------------------------------------------------")
    print("Press Ctrl+C at any time to gracefully terminate all services.\n")

    try:
        webbrowser.open("http://localhost:5173")
    except Exception:
        pass

    try:
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        signal_handler(None, None)

def interactive_menu():
    banner()
    while True:
        print("Please choose an option:")
        print(" [1] Start Full Application (MongoDB + Backend + Frontend + Browser)")
        print(" [2] Serve Built Production Client via Python (Port 5173)")
        print(" [3] Seed / Reset MongoDB Database")
        print(" [4] Run System Diagnostic & Port Check")
        print(" [5] Start Backend API Server Only (Port 5000)")
        print(" [0] Exit")
        print("-" * 50)
        
        try:
            choice = input("Enter selection [1-5, 0]: ").strip()
        except (KeyboardInterrupt, EOFError):
            print("\nExiting.")
            break

        if choice == "1":
            start_full_application()
            break
        elif choice == "2":
            serve_production(5173)
            break
        elif choice == "3":
            run_seed()
            print()
        elif choice == "4":
            check_system()
        elif choice == "5":
            ensure_mongodb()
            node_exe = find_executable(NODE_PATHS)
            env = os.environ.copy()
            env["PATH"] = r"C:\Program Files\nodejs;" + env.get("PATH", "")
            subprocess.run([node_exe, "server.js"], cwd=str(SERVER_DIR), env=env)
            break
        elif choice == "0":
            print("Exiting StaffSync Manager. Goodbye!")
            break
        else:
            print("Invalid selection, please try again.\n")

def main():
    parser = argparse.ArgumentParser(description="StaffSync HRMS Application Manager")
    parser.add_argument("--start", action="store_true", help="Launch entire application stack and open browser")
    parser.add_argument("--seed", action="store_true", help="Seed database with HR demo records")
    parser.add_argument("--check", action="store_true", help="Run system diagnostics and check port status")
    parser.add_argument("--serve", action="store_true", help="Serve production build using Python web server")
    parser.add_argument("--port", type=int, default=5173, help="Port to serve on (default: 5173)")

    args = parser.parse_args()

    if args.start:
        start_full_application()
    elif args.seed:
        ensure_mongodb()
        run_seed()
    elif args.check:
        banner()
        check_system()
    elif args.serve:
        serve_production(args.port)
    else:
        # Default behavior: run full application launch
        start_full_application()

if __name__ == "__main__":
    main()
