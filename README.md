# 🦁 LionBackup
**Automatic backup tool with a graphical interface, CLI, and system tray integration**

![Version](https://img.shields.io/badge/version-1.0.0-orange)
![Python](https://img.shields.io/badge/python-3.7+-blue)

---

## ⭐ Like the project
If you find LionBackup useful, consider leaving a ⭐ on the repository.

---

## 📋 Overview

LionBackup is a simple but reliable tool for automatically backing up files and folders.  
It is available in two versions:

- **GUI** — runs quietly in the background as a system tray application
- **CLI** — runs in the terminal with an interactive wizard or via arguments (great for scripts and automation)

Both versions create ZIP archives of your selected folders at scheduled intervals.  
The goal of the project is to provide an easy way to automate backups without dealing with complex setup or configuration.

---

## ✨ Features

- 🎨 **Simple GUI** — clean and easy-to-use interface
- ⌨️ **CLI with interactive wizard** — guided setup when run without arguments
- 🔄 **Automatic backups** — files are archived at regular intervals
- 📦 **ZIP compression** — backups are stored as compressed ZIP files
- 🔢 **Versioning** — automatic numbering prevents overwriting existing backups (`-2`, `-3`, `-4`, etc.)
- 💾 **System tray integration** — GUI runs quietly in the background
- ⏱️ **Flexible intervals** — set backups anywhere from 1 minute to 24 hours
- 🦁 **Custom design** — modern UI with a lion-themed style

---

## 🗂️ Project Structure

```
lionbackup/
├── core.py       ← Shared backup engine (no UI dependency)
├── gui.py        ← Tkinter GUI app
├── cli.py        ← Command-line interface
├── build.py      ← Build script (PyInstaller)
└── README.md
```

> `core.py` contains all backup logic and is completely UI-agnostic.  
> Both `gui.py` and `cli.py` use it — making it easy to add new frontends in the future.

---

## 🚀 Installation

### 1. Clone the repository
```bash
git clone https://github.com/liondevs/lionbackup.git
cd lionbackup
```

### 2. Install dependencies
```bash
pip install -r requirements.txt
```

### 3. Run the application

**GUI version:**
```bash
python gui.py
```

**CLI version (interactive wizard):**
```bash
python cli.py
```

**CLI version (direct arguments):**
```bash
# Backup once
python cli.py --source ./docs --dest ./backups --once

# Scheduled every 30 minutes
python cli.py --source ./docs --dest ./backups --interval 30
```

---

## ⌨️ CLI Options

| Flag | Short | Description |
|---|---|---|
| *(no arguments)* | | Launches interactive wizard |
| `--source` | `-s` | Folder to backup |
| `--dest` | `-d` | Destination folder for ZIP archives |
| `--interval` | `-i` | Interval in minutes (default: 60) |
| `--once` | | Run backup once and exit |
| `--version` | `-v` | Show version |

---

## 📦 Building .exe files

Use the included `build.py` script — it handles everything automatically.

```bash
# Build both GUI + CLI
python build.py

# Build only GUI  →  dist/LionBackup.exe
python build.py --gui

# Build only CLI  →  dist/lionbackup-cli.exe
python build.py --cli

# Clean previous builds first
python build.py --clean
```

### Manual builds (PyInstaller)

**GUI:**
```bash
pyinstaller --name="LionBackup" --onefile --windowed --icon=lion.ico --add-data "core.py;." gui.py
```

**CLI:**
```bash
pyinstaller --name="lionbackup-cli" --onefile --console --add-data "core.py;." cli.py
```

---

## 📞 Support

If you run into any issues or have questions:
- Open an **Issue** in the repository
- Email: **martin.kostadinov1337@gmail.com**

---

## 📄 License

This project is licensed under the **LionBackup Source License**.  
See the full license here: [LICENSE.md](LICENSE.md)
