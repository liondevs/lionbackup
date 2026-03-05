# 🦁 LionBackup

**Automatic backup tool with a graphical interface and system tray
integration**

![Version](https://img.shields.io/badge/version-1.0.0-orange)
![Python](https://img.shields.io/badge/python-3.7+-blue)

------------------------------------------------------------------------

## ⭐ Like the project

If you find LionBackup useful, consider leaving a ⭐ on the repository.

------------------------------------------------------------------------

## 📋 Overview

LionBackup is a simple but reliable tool for automatically backing up
files and folders.
It runs quietly in the background as a system tray application and
creates ZIP archives of your selected files at scheduled intervals.

The goal of the project is to provide an easy way to automate backups
without dealing with complex setup or configuration.

------------------------------------------------------------------------

## ✨ Features

-   🎨 **Simple GUI** -- clean and easy-to-use interface
-   🔄 **Automatic backups** -- files are archived at regular intervals
-   📦 **ZIP compression** -- backups are stored as compressed ZIP
    files
-   🔢 **Versioning** -- automatic numbering prevents overwriting
    existing backups (`-2`, `-3`, `-4`, etc.)
-   💾 **System tray integration** -- runs quietly in the background
-   ⏱️ **Flexible intervals** -- set backups anywhere from 1 minute to
    24 hours
-   🦁 **Custom design** -- modern UI with a lion-themed style

------------------------------------------------------------------------

## 🚀 Installation

### 1. Clone the repository

``` bash
git clone https://github.com/liondevs/lionbackup.git
cd lionbackup
```

### 2. Install dependencies

``` bash
pip install -r requirements.txt
```

### 3. Run the application

``` bash
python lionbackup.py
```

Run without opening a terminal window:

``` bash
python lionbackup.py
```

------------------------------------------------------------------------

## 📦 Building a .exe

### Method 1 --- Basic build (faster)

``` bash
pyinstaller --name="LionBackup" --onefile --windowed --icon=lion.ico lionbackup.py
```

### Method 2 --- Optimized build (recommended)

``` bash
pyinstaller --name="LionBackup" ^
            --onefile ^
            --windowed ^
            --icon=lion.ico ^
            --add-data "icon.png;." ^
            --hidden-import=PIL ^
            --hidden-import=pystray ^
            --noconsole ^
            --clean ^
            lionbackup.py
```

------------------------------------------------------------------------

## 📞 Support

If you run into any issues or have questions:

-   Open an **Issue** in the repository
-   Email: **martin.kostadinov1337@gmail.com**

## 📄 License

This project is licensed under the **LionBackup Source License**.

See the full license here:  
[LICENSE.md](LICENSE.md)
