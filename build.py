"""
LionBackup Build Script
Builds GUI and/or CLI versions using PyInstaller

Usage:
  python build.py           # build both
  python build.py --gui     # build only GUI
  python build.py --cli     # build only CLI
  python build.py --clean   # remove previous builds first
"""

import subprocess
import sys
import shutil
import os
import argparse

# ----------------------------------------------------------------- Config ---

APP_NAME_GUI = "LionBackup"
APP_NAME_CLI = "lionbackup-cli"
DIST_DIR     = "dist"
BUILD_DIR    = "build"
ICON_PATH    = "icon.ico"       # optional — place icon.ico next to build.py

COMMON_FLAGS = [
    "--noconfirm",
    "--clean",
    "--onefile",
    f"--add-data=core.py{os.pathsep}.",
]

GUI_FLAGS = [
    f"--name={APP_NAME_GUI}",
    "--windowed",               # no console window on Windows
    "gui.py",
]

CLI_FLAGS = [
    f"--name={APP_NAME_CLI}",
    "--console",                # keep console for CLI
    "cli.py",
]

# ----------------------------------------------------------------- Helpers --

def run(cmd: list[str]):
    print(f"\n  ► {' '.join(cmd)}\n")
    result = subprocess.run(cmd, check=False)
    if result.returncode != 0:
        print(f"\n  ✗ Build failed (exit code {result.returncode})")
        sys.exit(result.returncode)


def clean():
    for d in (DIST_DIR, BUILD_DIR):
        if os.path.exists(d):
            shutil.rmtree(d)
            print(f"  Removed: {d}/")
    for f in os.listdir("."):
        if f.endswith(".spec"):
            os.remove(f)
            print(f"  Removed: {f}")


def check_pyinstaller():
    if shutil.which("pyinstaller") is None:
        print("  PyInstaller not found. Installing...")
        subprocess.run(
            [sys.executable, "-m", "pip", "install", "pyinstaller"],
            check=True
        )


def build_gui():
    print("\n  ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━")
    print("  🖥  Building GUI version...")
    print("  ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━\n")

    flags = COMMON_FLAGS + GUI_FLAGS
    if os.path.exists(ICON_PATH):
        flags = [f"--icon={ICON_PATH}"] + flags

    run(["pyinstaller"] + flags)
    print(f"\n  ✓ GUI build → {DIST_DIR}/{APP_NAME_GUI}")


def build_cli():
    print("\n  ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━")
    print("  ⌨   Building CLI version...")
    print("  ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━\n")

    flags = COMMON_FLAGS + CLI_FLAGS
    run(["pyinstaller"] + flags)
    print(f"\n  ✓ CLI build → {DIST_DIR}/{APP_NAME_CLI}")


def print_summary():
    print("\n  ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━")
    print("  🦁 Build complete! Outputs:")
    for name in (APP_NAME_GUI, APP_NAME_CLI):
        exe = os.path.join(DIST_DIR, name)
        if sys.platform == "win32":
            exe += ".exe"
        if os.path.exists(exe):
            size = os.path.getsize(exe) / (1024 * 1024)
            print(f"     {exe}  ({size:.1f} MB)")
    print("  ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━\n")


# ------------------------------------------------------------------- Main ---

def main():
    parser = argparse.ArgumentParser(
        description="🦁 LionBackup build script",
        formatter_class=argparse.RawTextHelpFormatter
    )
    parser.add_argument("--gui",   action="store_true", help="Build GUI only")
    parser.add_argument("--cli",   action="store_true", help="Build CLI only")
    parser.add_argument("--clean", action="store_true", help="Clean before building")
    args = parser.parse_args()

    # Default: build both
    build_both = not args.gui and not args.cli

    check_pyinstaller()

    if args.clean:
        clean()

    if build_both or args.gui:
        build_gui()

    if build_both or args.cli:
        build_cli()

    print_summary()


if __name__ == "__main__":
    main()
