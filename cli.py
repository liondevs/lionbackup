"""
LionBackup CLI
- No args → interactive wizard
- With args → direct mode (scriptable)
Author: liondevs (Martin Kostadinov)
"""

import argparse
import sys
import signal
import time
import os
from core import BackupEngine

# ANSI colors
GREEN  = "\033[92m"
YELLOW = "\033[93m"
RED    = "\033[91m"
CYAN   = "\033[96m"
DIM    = "\033[2m"
BOLD   = "\033[1m"
RESET  = "\033[0m"

BANNER = f"""{BOLD}
  ██╗     ██╗ ██████╗ ███╗   ██╗██████╗  █████╗  ██████╗██╗  ██╗██╗   ██╗██████╗ 
  ██║     ██║██╔═══██╗████╗  ██║██╔══██╗██╔══██╗██╔════╝██║ ██╔╝██║   ██║██╔══██╗
  ██║     ██║██║   ██║██╔██╗ ██║██████╔╝███████║██║     █████╔╝ ██║   ██║██████╔╝
  ██║     ██║██║   ██║██║╚██╗██║██╔══██╗██╔══██║██║     ██╔═██╗ ██║   ██║██╔═══╝ 
  ███████╗██║╚██████╔╝██║ ╚████║██████╔╝██║  ██║╚██████╗██║  ██╗╚██████╔╝██║     
  ╚══════╝╚═╝ ╚═════╝ ╚═╝  ╚═══╝╚═════╝ ╚═╝  ╚═╝ ╚═════╝╚═╝  ╚═╝ ╚═════╝ ╚═╝     
{RESET}{CYAN}  Auto Files Backup  |  by liondevs (Martin Kostadinov){RESET}
"""

DIVIDER = f"  {DIM}{'─' * 50}{RESET}"


# ----------------------------------------------------------------- Output ---

def print_status(message: str, level: str = "info"):
    ts = time.strftime("%H:%M:%S")
    icons = {
        "success": f"{GREEN}✓{RESET}",
        "warning": f"{YELLOW}⚠{RESET}",
        "error":   f"{RED}✗{RESET}",
        "info":    f"{CYAN}•{RESET}",
    }
    prefix = icons.get(level, icons["info"])
    print(f"  [{ts}] {prefix}  {message}")


def print_error(message: str):
    print_status(message, "error")


def ask(prompt: str, default: str = "") -> str:
    """Prompt user for input, with optional default value."""
    default_hint = f"{DIM}[{default}]{RESET} " if default else ""
    try:
        value = input(f"  {CYAN}?{RESET}  {prompt} {default_hint}› ").strip()
    except (KeyboardInterrupt, EOFError):
        print(f"\n\n  {YELLOW}Cancelled.{RESET}\n")
        sys.exit(0)
    return value if value else default


def ask_choice(prompt: str, choices: list, default: str) -> str:
    """Show a numbered menu and return the chosen value."""
    print(f"\n  {CYAN}?{RESET}  {prompt}")
    for i, (val, label) in enumerate(choices, 1):
        marker = f"{GREEN}●{RESET}" if val == default else f"{DIM}○{RESET}"
        print(f"     {marker} {i}) {label}")

    default_num = str(next(i for i, (v, _) in enumerate(choices, 1) if v == default))
    while True:
        raw = ask("Enter number", default_num)
        if raw.isdigit():
            idx = int(raw) - 1
            if 0 <= idx < len(choices):
                return choices[idx][0]
        print(f"  {RED}✗{RESET}  Please enter a number between 1 and {len(choices)}")


def confirm(prompt: str, default: bool = True) -> bool:
    hint = "Y/n" if default else "y/N"
    raw = ask(f"{prompt} ({hint})", "").lower()
    if raw == "":
        return default
    return raw in ("y", "yes")


# --------------------------------------------------------------- Wizard ----

def interactive_wizard() -> dict:
    """Guides the user through setup interactively."""
    print(f"\n{DIVIDER}")
    print(f"  {BOLD}Welcome! Let's set up your backup.{RESET}")
    print(f"  {DIM}Press Enter to accept defaults  |  Ctrl+C to cancel{RESET}")
    print(DIVIDER)

    # --- Source folder ---
    print()
    while True:
        source = ask("Folder to backup (full path)")
        if not source:
            print(f"  {RED}✗{RESET}  Path cannot be empty.")
            continue
        source = os.path.normpath(source.strip('"').strip("'"))
        if not os.path.isdir(source):
            print(f"  {RED}✗{RESET}  Folder not found: {source}")
            if not confirm("   Create it?", default=False):
                continue
            try:
                os.makedirs(source)
                print(f"  {GREEN}✓{RESET}  Created: {source}")
            except Exception as e:
                print(f"  {RED}✗{RESET}  Could not create folder: {e}")
                continue
        print(f"  {GREEN}✓{RESET}  Source: {BOLD}{source}{RESET}")
        break

    # --- Destination folder ---
    print()
    while True:
        dest = ask("Where to save backups (full path)")
        if not dest:
            print(f"  {RED}✗{RESET}  Path cannot be empty.")
            continue
        dest = os.path.normpath(dest.strip('"').strip("'"))
        if not os.path.isdir(dest):
            print(f"  {YELLOW}⚠{RESET}  Folder doesn't exist: {dest}")
            if confirm("   Create it?", default=True):
                try:
                    os.makedirs(dest)
                    print(f"  {GREEN}✓{RESET}  Created: {dest}")
                except Exception as e:
                    print(f"  {RED}✗{RESET}  Could not create folder: {e}")
                    continue
            else:
                continue
        print(f"  {GREEN}✓{RESET}  Destination: {BOLD}{dest}{RESET}")
        break

    # --- Mode ---
    mode = ask_choice(
        "Backup mode",
        choices=[
            ("scheduled", "Scheduled  — runs automatically every X minutes"),
            ("once",      "Run once   — backup now and exit"),
        ],
        default="scheduled"
    )

    interval = 60
    if mode == "scheduled":
        print()
        while True:
            raw = ask("Interval in minutes", "60")
            if raw.isdigit() and int(raw) >= 1:
                interval = int(raw)
                break
            print(f"  {RED}✗{RESET}  Please enter a whole number >= 1")

    # --- Summary ---
    print(f"\n{DIVIDER}")
    print(f"  {BOLD}Summary{RESET}")
    print(f"  Source   : {source}")
    print(f"  Dest     : {dest}")
    if mode == "scheduled":
        print(f"  Mode     : Scheduled every {interval} minute(s)")
    else:
        print(f"  Mode     : Single backup")
    print(DIVIDER)

    if not confirm("\n  Start backup?", default=True):
        print(f"\n  {YELLOW}Cancelled.{RESET}\n")
        sys.exit(0)

    print()
    return {"source": source, "dest": dest, "interval": interval, "once": mode == "once"}


# ----------------------------------------------------------------- Args ----

def parse_args():
    parser = argparse.ArgumentParser(
        prog="lionbackup-cli",
        description="LionBackup — run without arguments for interactive mode",
        formatter_class=argparse.RawTextHelpFormatter,
        epilog="""
Examples:
  lionbackup-cli                                   # interactive wizard
  lionbackup-cli -s ./docs -d ./backups --once     # backup once
  lionbackup-cli -s ./docs -d ./backups -i 30      # every 30 min
"""
    )
    parser.add_argument("--source",   "-s", metavar="PATH",    help="Folder to backup")
    parser.add_argument("--dest",     "-d", metavar="PATH",    help="Destination folder")
    parser.add_argument("--interval", "-i", metavar="MINUTES", type=int, default=60,
                        help="Interval in minutes (default: 60)")
    parser.add_argument("--once",           action="store_true", help="Run once and exit")
    parser.add_argument("--version",  "-v", action="version",  version="LionBackup 1.0.0 | liondevs")
    return parser.parse_args()


# ----------------------------------------------------------------- Run -----

def run_backup(source: str, dest: str, interval: int, once: bool):
    engine = BackupEngine()
    engine.set_status_callback(print_status)
    engine.set_error_callback(print_error)

    if once:
        success = engine.create_backup(source, dest)
        print()
        sys.exit(0 if success else 1)
    else:
        print(f"  {BOLD}Running{RESET} — {YELLOW}Ctrl+C to stop{RESET}\n")

        def handle_signal(sig, frame):
            print(f"\n  {YELLOW}Stopping LionBackup...{RESET}\n")
            engine.stop_scheduled()
            sys.exit(0)

        signal.signal(signal.SIGINT, handle_signal)
        signal.signal(signal.SIGTERM, handle_signal)

        engine.start_scheduled(source, dest, interval)

        try:
            while engine.is_running:
                time.sleep(1)
        except KeyboardInterrupt:
            engine.stop_scheduled()


def main():
    print(BANNER)
    args = parse_args()

    # No arguments → interactive wizard
    if not args.source and not args.dest:
        config = interactive_wizard()
    else:
        # Direct mode — validate required flags
        if not args.source:
            print(f"  {RED}✗{RESET}  --source is required in direct mode\n")
            sys.exit(1)
        if not args.dest:
            print(f"  {RED}✗{RESET}  --dest is required in direct mode\n")
            sys.exit(1)
        config = {
            "source":   args.source,
            "dest":     args.dest,
            "interval": args.interval,
            "once":     args.once,
        }

    run_backup(**config)


if __name__ == "__main__":
    main()
