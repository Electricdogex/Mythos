#!/usr/bin/env python3
"""
Mythos 522026 Alpha

Tiny VPS program runner.

Naming sequence:
- 522026 = month/day/year = 5/2/2026
- Alpha = early development build

Features:
- EULA-gated usage
- Program-based config
- Backward-compatible migration from old "services" configs
- PM2 install/update helpers
- Basic program logs and PID management
"""

from __future__ import annotations

import argparse
import json
import os
import platform
import shutil
import signal
import subprocess
import sys
import time
from dataclasses import dataclass
from pathlib import Path
from typing import Any


VERSION = "522026-alpha"
VERSION_NAME = "Mythos 522026 Alpha"

BASE_DIR = Path(__file__).resolve().parent
CONFIG_FILE = BASE_DIR / "mythos.json"
EULA_FILE = BASE_DIR / "EULA.md"
RUNTIME_DIR = BASE_DIR / ".mythos"
PID_DIR = RUNTIME_DIR / "pids"
LOG_DIR = RUNTIME_DIR / "logs"
EULA_ACCEPTED_FILE = RUNTIME_DIR / "eula_accepted.json"


@dataclass
class Program:
    name: str
    command: str
    cwd: Path
    env: dict[str, str]
    autostart: bool = True
    restart: str = "never"


def ensure_dirs() -> None:
    PID_DIR.mkdir(parents=True, exist_ok=True)
    LOG_DIR.mkdir(parents=True, exist_ok=True)


def default_config() -> dict[str, Any]:
    return {
        "name": "Mythos",
        "version": VERSION,
        "programs": []
    }


def normalize_config(data: dict[str, Any]) -> dict[str, Any]:
    if "programs" not in data and "services" in data:
        data["programs"] = data["services"]

    if "programs" not in data:
        data["programs"] = []

    data["version"] = VERSION

    if "services" in data:
        del data["services"]

    return data


def load_config() -> dict[str, Any]:
    if not CONFIG_FILE.exists():
        return default_config()

    try:
        with CONFIG_FILE.open("r", encoding="utf-8") as f:
            data = json.load(f)
    except json.JSONDecodeError as err:
        print(f"Config error in {CONFIG_FILE}: {err}", file=sys.stderr)
        sys.exit(1)

    data = normalize_config(data)

    if "programs" not in data or not isinstance(data["programs"], list):
        print("Config error: mythos.json must contain a 'programs' list.", file=sys.stderr)
        sys.exit(1)

    return data


def save_config(data: dict[str, Any]) -> None:
    data = normalize_config(data)
    CONFIG_FILE.write_text(json.dumps(data, indent=2), encoding="utf-8")


def program_from_dict(item: dict[str, Any]) -> Program:
    name = str(item.get("name", "")).strip()
    command = str(item.get("command", "")).strip()
    cwd_raw = str(item.get("cwd", ".")).strip() or "."

    if not name:
        raise ValueError("A program is missing its name.")
    if not command:
        raise ValueError(f"Program '{name}' is missing its command.")

    env = item.get("env", {})
    if not isinstance(env, dict):
        raise ValueError(f"Program '{name}' has invalid env. It must be an object.")

    return Program(
        name=name,
        command=command,
        cwd=(BASE_DIR / cwd_raw).resolve() if not Path(cwd_raw).is_absolute() else Path(cwd_raw),
        env={str(k): str(v) for k, v in env.items()},
        autostart=bool(item.get("autostart", True)),
        restart=str(item.get("restart", "never")).lower(),
    )


def get_programs() -> list[Program]:
    data = load_config()
    programs: list[Program] = []

    for raw in data["programs"]:
        if not isinstance(raw, dict):
            print("Config error: each program must be an object.", file=sys.stderr)
            sys.exit(1)
        try:
            programs.append(program_from_dict(raw))
        except ValueError as err:
            print(f"Config error: {err}", file=sys.stderr)
            sys.exit(1)

    return programs


def find_program(name: str) -> Program:
    for program in get_programs():
        if program.name == name:
            return program

    print(f"No program named '{name}' exists in mythos.json.", file=sys.stderr)
    sys.exit(1)


def safe_name(program_name: str) -> str:
    return "".join(c for c in program_name if c.isalnum() or c in ("-", "_", "."))


def pid_file(program_name: str) -> Path:
    return PID_DIR / f"{safe_name(program_name)}.pid"


def log_file(program_name: str) -> Path:
    return LOG_DIR / f"{safe_name(program_name)}.log"


def read_pid(program_name: str) -> int | None:
    path = pid_file(program_name)
    if not path.exists():
        return None

    try:
        return int(path.read_text(encoding="utf-8").strip())
    except ValueError:
        path.unlink(missing_ok=True)
        return None


def process_alive(pid: int) -> bool:
    try:
        os.kill(pid, 0)
    except ProcessLookupError:
        return False
    except PermissionError:
        return True
    return True


def is_running(program_name: str) -> tuple[bool, int | None]:
    pid = read_pid(program_name)
    if pid is None:
        return False, None

    if process_alive(pid):
        return True, pid

    pid_file(program_name).unlink(missing_ok=True)
    return False, None


def run_shell(command: str, check: bool = True) -> int:
    print(f"$ {command}")
    proc = subprocess.run(command, shell=True)
    if check and proc.returncode != 0:
        print(f"Command failed with exit code {proc.returncode}.", file=sys.stderr)
        sys.exit(proc.returncode)
    return proc.returncode


def eula_text() -> str:
    if EULA_FILE.exists():
        return EULA_FILE.read_text(encoding="utf-8", errors="replace")

    return "# Mythos EULA\n\nYou must accept the Mythos EULA before using Mythos.\n"


def eula_is_accepted() -> bool:
    if not EULA_ACCEPTED_FILE.exists():
        return False

    try:
        data = json.loads(EULA_ACCEPTED_FILE.read_text(encoding="utf-8"))
    except Exception:
        return False

    return data.get("accepted") is True and data.get("version") == VERSION


def write_eula_acceptance() -> None:
    ensure_dirs()
    EULA_ACCEPTED_FILE.write_text(
        json.dumps(
            {
                "accepted": True,
                "version": VERSION,
                "accepted_at": time.ctime(),
                "eula_file": str(EULA_FILE),
            },
            indent=2,
        ),
        encoding="utf-8",
    )


def require_eula() -> None:
    if eula_is_accepted():
        return

    print("Mythos EULA has not been accepted yet.")
    print("Read it with:")
    print("  ./mythos.py eula")
    print("Accept it with:")
    print("  ./mythos.py accept-eula")
    sys.exit(2)


def start_program(program: Program) -> None:
    ensure_dirs()

    running, pid = is_running(program.name)
    if running:
        print(f"{program.name} is already running. PID: {pid}")
        return

    if not program.cwd.exists():
        print(f"Cannot start {program.name}: cwd does not exist: {program.cwd}", file=sys.stderr)
        sys.exit(1)

    env = os.environ.copy()
    env.update(program.env)

    lf = log_file(program.name)
    log_handle = lf.open("ab", buffering=0)
    log_handle.write(f"\n--- Mythos starting {program.name} at {time.ctime()} ---\n".encode("utf-8"))

    try:
        proc = subprocess.Popen(
            program.command,
            shell=True,
            cwd=str(program.cwd),
            env=env,
            stdout=log_handle,
            stderr=subprocess.STDOUT,
            stdin=subprocess.DEVNULL,
            start_new_session=True,
        )
    except Exception as err:
        print(f"Failed to start {program.name}: {err}", file=sys.stderr)
        sys.exit(1)

    pid_file(program.name).write_text(str(proc.pid), encoding="utf-8")
    print(f"Started {program.name}. PID: {proc.pid}")
    print(f"Log: {lf}")


def stop_program(program_name: str, timeout: float = 10.0) -> None:
    running, pid = is_running(program_name)
    if not running or pid is None:
        print(f"{program_name} is not running.")
        return

    print(f"Stopping {program_name}. PID: {pid}")

    try:
        os.killpg(pid, signal.SIGTERM)
    except ProcessLookupError:
        pid_file(program_name).unlink(missing_ok=True)
        print(f"{program_name} was already stopped.")
        return
    except PermissionError:
        print(f"Permission denied while stopping {program_name}. Try running with sudo/root.", file=sys.stderr)
        sys.exit(1)

    deadline = time.time() + timeout
    while time.time() < deadline:
        if not process_alive(pid):
            pid_file(program_name).unlink(missing_ok=True)
            print(f"Stopped {program_name}.")
            return
        time.sleep(0.25)

    print(f"{program_name} did not stop cleanly. Killing it now.")
    try:
        os.killpg(pid, signal.SIGKILL)
    except ProcessLookupError:
        pass

    pid_file(program_name).unlink(missing_ok=True)
    print(f"Killed {program_name}.")


def status_program(program: Program) -> None:
    running, pid = is_running(program.name)
    state = "running" if running else "stopped"
    pid_text = str(pid) if pid else "-"
    print(f"{program.name:24} {state:10} PID: {pid_text}")


def tail_log(program_name: str, lines: int = 80) -> None:
    lf = log_file(program_name)
    if not lf.exists():
        print(f"No log exists yet for {program_name}.")
        return

    content = lf.read_text(encoding="utf-8", errors="replace").splitlines()
    for line in content[-lines:]:
        print(line)


def cmd_version(_: argparse.Namespace) -> None:
    print(VERSION_NAME)
    print(f"Build: {VERSION}")
    print(f"Python {platform.python_version()}")
    print(f"Folder: {BASE_DIR}")
    print(f"EULA accepted: {'yes' if eula_is_accepted() else 'no'}")


def cmd_eula(_: argparse.Namespace) -> None:
    print(eula_text())


def cmd_accept_eula(args: argparse.Namespace) -> None:
    text = eula_text()

    if not args.yes:
        print(text)
        print("")
        answer = input("Type ACCEPT to accept the Mythos EULA: ").strip()
        if answer != "ACCEPT":
            print("EULA was not accepted.")
            sys.exit(1)

    write_eula_acceptance()
    print("Mythos EULA accepted.")


def cmd_init(_: argparse.Namespace) -> None:
    require_eula()
    ensure_dirs()

    if CONFIG_FILE.exists():
        print(f"{CONFIG_FILE} already exists.")
        return

    save_config(default_config())
    print(f"Created empty Mythos config: {CONFIG_FILE}")
    print("Add programs to mythos.json, then run: ./mythos.py start")


def cmd_start(args: argparse.Namespace) -> None:
    require_eula()
    programs = get_programs()

    if args.name:
        start_program(find_program(args.name))
        return

    started_any = False
    for program in programs:
        if program.autostart:
            start_program(program)
            started_any = True

    if not programs:
        print("No programs configured yet. Add programs to mythos.json.")
    elif not started_any:
        print("No autostart programs found. Start one with: ./mythos.py start <name>")


def cmd_stop(args: argparse.Namespace) -> None:
    require_eula()

    if args.name:
        stop_program(args.name)
        return

    programs = get_programs()
    if not programs:
        print("No programs configured.")
        return

    for program in programs:
        stop_program(program.name)


def cmd_restart(args: argparse.Namespace) -> None:
    require_eula()

    if args.name:
        program = find_program(args.name)
        stop_program(program.name)
        start_program(program)
        return

    programs = get_programs()
    if not programs:
        print("No programs configured.")
        return

    for program in programs:
        stop_program(program.name)
        start_program(program)


def cmd_status(_: argparse.Namespace) -> None:
    require_eula()

    programs = get_programs()
    if not programs:
        print("No programs configured yet.")
        return

    for program in programs:
        status_program(program)


def cmd_logs(args: argparse.Namespace) -> None:
    require_eula()
    tail_log(args.name, args.lines)


def cmd_list(_: argparse.Namespace) -> None:
    require_eula()

    programs = get_programs()
    if not programs:
        print("No programs configured yet.")
        return

    for program in programs:
        print(f"{program.name}")
        print(f"  command: {program.command}")
        print(f"  cwd:     {program.cwd}")
        print(f"  start:   {'auto' if program.autostart else 'manual'}")
        print(f"  restart: {program.restart}")


def cmd_add(args: argparse.Namespace) -> None:
    require_eula()

    data = load_config()

    for item in data["programs"]:
        if item.get("name") == args.name:
            print(f"A program named '{args.name}' already exists.", file=sys.stderr)
            sys.exit(1)

    data["programs"].append({
        "name": args.name,
        "command": args.command,
        "cwd": args.cwd,
        "autostart": not args.manual,
        "restart": "never",
        "env": {}
    })

    save_config(data)
    print(f"Added program '{args.name}' to mythos.json.")


def cmd_remove(args: argparse.Namespace) -> None:
    require_eula()

    data = load_config()
    old_len = len(data["programs"])
    data["programs"] = [p for p in data["programs"] if p.get("name") != args.name]

    if len(data["programs"]) == old_len:
        print(f"No program named '{args.name}' exists in mythos.json.")
        return

    save_config(data)
    pid_file(args.name).unlink(missing_ok=True)
    print(f"Removed program '{args.name}' from mythos.json.")


def cmd_install_pm2(args: argparse.Namespace) -> None:
    require_eula()

    print("Mythos PM2 installer")
    print("This installs Node.js/npm through apt if missing, then installs or updates PM2 globally through npm.")

    if os.geteuid() != 0:
        print("Warning: PM2 auto-install may need sudo/root permissions.")

    if shutil.which("node") is None or shutil.which("npm") is None:
        run_shell("apt update")
        run_shell("apt install -y nodejs npm")
    else:
        print("Node.js and npm are already installed.")

    run_shell("npm install -g pm2@latest")
    print("PM2 is installed/updated.")
    run_shell("pm2 --version", check=False)

    if args.startup:
        print("\nGenerating PM2 startup command.")
        print("PM2 may print another command you need to copy/paste.")
        run_shell("pm2 startup", check=False)


def cmd_update_pm2(args: argparse.Namespace) -> None:
    require_eula()

    print("Updating PM2...")
    run_shell("npm install -g pm2@latest")
    run_shell("pm2 update", check=False)
    run_shell("pm2 --version", check=False)
    if args.save:
        run_shell("pm2 save", check=False)


def cmd_pm2_status(_: argparse.Namespace) -> None:
    require_eula()

    if shutil.which("pm2") is None:
        print("PM2 is not installed. Run: ./mythos.py install-pm2")
        return
    run_shell("pm2 status", check=False)


def cmd_make_test(args: argparse.Namespace) -> None:
    require_eula()

    test_path = BASE_DIR / "examples" / "test_program.py"
    if not test_path.exists():
        print(f"Missing test program: {test_path}", file=sys.stderr)
        sys.exit(1)

    data = load_config()
    name = args.name

    for item in data["programs"]:
        if item.get("name") == name:
            print(f"Program '{name}' already exists.")
            return

    data["programs"].append({
        "name": name,
        "command": "python3 examples/test_program.py",
        "cwd": ".",
        "autostart": True,
        "restart": "never",
        "env": {}
    })
    save_config(data)
    print(f"Added test program '{name}'.")
    print("Run it with:")
    print(f"  ./mythos.py start {name}")
    print(f"  ./mythos.py logs {name}")
    print(f"  ./mythos.py stop {name}")


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="mythos",
        description="Tiny VPS program runner with PM2 helper tools."
    )

    sub = parser.add_subparsers(dest="command", required=True)

    p = sub.add_parser("version", help="Show Mythos version.")
    p.set_defaults(func=cmd_version)

    p = sub.add_parser("eula", help="Read the Mythos EULA.")
    p.set_defaults(func=cmd_eula)

    p = sub.add_parser("accept-eula", help="Accept the Mythos EULA.")
    p.add_argument("--yes", action="store_true", help="Accept without interactive prompt.")
    p.set_defaults(func=cmd_accept_eula)

    p = sub.add_parser("init", help="Create an empty mythos.json config.")
    p.set_defaults(func=cmd_init)

    p = sub.add_parser("start", help="Start all autostart programs or one program.")
    p.add_argument("name", nargs="?", help="Optional program name.")
    p.set_defaults(func=cmd_start)

    p = sub.add_parser("stop", help="Stop all programs or one program.")
    p.add_argument("name", nargs="?", help="Optional program name.")
    p.set_defaults(func=cmd_stop)

    p = sub.add_parser("restart", help="Restart all programs or one program.")
    p.add_argument("name", nargs="?", help="Optional program name.")
    p.set_defaults(func=cmd_restart)

    p = sub.add_parser("status", help="Show program status.")
    p.set_defaults(func=cmd_status)

    p = sub.add_parser("logs", help="Show recent logs for a program.")
    p.add_argument("name", help="Program name.")
    p.add_argument("--lines", type=int, default=80, help="Number of lines to show.")
    p.set_defaults(func=cmd_logs)

    p = sub.add_parser("list", help="List configured programs.")
    p.set_defaults(func=cmd_list)

    p = sub.add_parser("add", help="Add a program entry to mythos.json.")
    p.add_argument("name", help="Program name.")
    p.add_argument("command", help="Command to run.")
    p.add_argument("--cwd", default=".", help="Working directory. Default: current Mythos folder.")
    p.add_argument("--manual", action="store_true", help="Do not start with './mythos.py start'.")
    p.set_defaults(func=cmd_add)

    p = sub.add_parser("remove", help="Remove a program from mythos.json.")
    p.add_argument("name", help="Program name.")
    p.set_defaults(func=cmd_remove)

    p = sub.add_parser("make-test", help="Add the included Mythos test program.")
    p.add_argument("--name", default="mythos-test", help="Program name. Default: mythos-test")
    p.set_defaults(func=cmd_make_test)

    p = sub.add_parser("install-pm2", help="Install Node.js/npm if needed, then install or update PM2.")
    p.add_argument("--startup", action="store_true", help="Also run pm2 startup after install.")
    p.set_defaults(func=cmd_install_pm2)

    p = sub.add_parser("update-pm2", help="Update PM2 to latest version.")
    p.add_argument("--save", action="store_true", help="Run pm2 save after updating.")
    p.set_defaults(func=cmd_update_pm2)

    p = sub.add_parser("pm2-status", help="Show PM2 status if PM2 is installed.")
    p.set_defaults(func=cmd_pm2_status)

    return parser


def main() -> None:
    ensure_dirs()
    parser = build_parser()
    args = parser.parse_args()
    args.func(args)


if __name__ == "__main__":
    main()
