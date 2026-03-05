"""
LionBackup GUI
Tkinter interface using the shared BackupEngine core
Author: liondevs (Martin Kostadinov)
"""

import tkinter as tk
from tkinter import filedialog, messagebox, ttk
import threading
from PIL import Image, ImageDraw
import pystray
from pystray import MenuItem as item

from core import BackupEngine


class LionBackupApp:
    def __init__(self):
        self.window = tk.Tk()
        self.window.title("LionBackup")
        self.window.geometry("500x480")
        self.window.resizable(False, False)
        self.window.protocol("WM_DELETE_WINDOW", self.hide_window)

        self.source_folder = tk.StringVar()
        self.dest_folder = tk.StringVar()
        self.backup_interval = tk.IntVar(value=60)
        self.tray_icon = None

        # Wire up the core engine
        self.engine = BackupEngine()
        self.engine.set_status_callback(self._on_status)
        self.engine.set_error_callback(self._on_error)

        self.create_gui()

    # ------------------------------------------------------------------ GUI --

    def create_gui(self):
        # Header
        tk.Label(self.window, text="🦁 LionBackup",
                 font=("Arial", 18, "bold"), fg="#FF6B00").pack(pady=10)
        tk.Label(self.window, text="Auto Files Backup",
                 font=("Arial", 9), fg="gray").pack()

        # Source folder
        source_frame = tk.Frame(self.window)
        source_frame.pack(pady=10, padx=20, fill="x")
        tk.Label(source_frame, text="Folder to backup:",
                 font=("Arial", 10)).pack(anchor="w")
        sef = tk.Frame(source_frame)
        sef.pack(fill="x")
        tk.Entry(sef, textvariable=self.source_folder,
                 width=40).pack(side="left", fill="x", expand=True)
        tk.Button(sef, text="Choose",
                  command=self.browse_source).pack(side="left", padx=5)

        # Destination folder
        dest_frame = tk.Frame(self.window)
        dest_frame.pack(pady=10, padx=20, fill="x")
        tk.Label(dest_frame, text="Where to save:",
                 font=("Arial", 10)).pack(anchor="w")
        def_ = tk.Frame(dest_frame)
        def_.pack(fill="x")
        tk.Entry(def_, textvariable=self.dest_folder,
                 width=40).pack(side="left", fill="x", expand=True)
        tk.Button(def_, text="Choose",
                  command=self.browse_dest).pack(side="left", padx=5)

        # Interval
        interval_frame = tk.Frame(self.window)
        interval_frame.pack(pady=10, padx=20, fill="x")
        tk.Label(interval_frame, text="Backup interval (minutes):",
                 font=("Arial", 10)).pack(anchor="w")
        tk.Spinbox(interval_frame, from_=1, to=1440,
                   textvariable=self.backup_interval,
                   width=10).pack(anchor="w", pady=5)

        # Buttons
        button_frame = tk.Frame(self.window)
        button_frame.pack(pady=15)
        self.start_button = tk.Button(
            button_frame, text="▶ Start", command=self.start_backup,
            bg="#FF6B00", fg="white", font=("Arial", 12, "bold"), width=12)
        self.start_button.pack(side="left", padx=5)
        self.stop_button = tk.Button(
            button_frame, text="⏸ Stop", command=self.stop_backup,
            bg="#f44336", fg="white", font=("Arial", 12, "bold"),
            width=12, state="disabled")
        self.stop_button.pack(side="left", padx=5)

        # Status
        self.status_label = tk.Label(self.window, text="Status: Disabled",
                                     font=("Arial", 10), fg="gray")
        self.status_label.pack(pady=10)

        # Progress bar
        self.progress = ttk.Progressbar(self.window, mode='indeterminate')
        self.progress.pack(pady=5, padx=20, fill="x")

        # Spacer + footer
        tk.Frame(self.window, height=20).pack(fill="both", expand=True)
        footer = tk.Frame(self.window, bg="#2c3e50", height=35)
        footer.pack(side="bottom", fill="x")
        footer.pack_propagate(False)
        tk.Label(footer, text="Author: liondevs (Martin Kostadinov)",
                 font=("Arial", 9, "bold"), bg="#2c3e50", fg="#ecf0f1").pack(expand=True)

    # ---------------------------------------------------------- Callbacks --

    def _on_status(self, message: str, level: str):
        """Called by BackupEngine on status updates"""
        color_map = {
            "success": "green",
            "warning": "orange",
            "error":   "red",
            "info":    "blue",
        }
        color = color_map.get(level, "black")
        self.window.after(0, self._update_status_label, message, color)

    def _on_error(self, message: str):
        self._on_status(message, "error")

    def _update_status_label(self, message: str, color: str):
        try:
            if self.status_label.winfo_exists():
                self.status_label.config(text=f"Status: {message}", fg=color)
        except Exception:
            pass

    # ----------------------------------------------------------- Actions --

    def browse_source(self):
        folder = filedialog.askdirectory(title="Choose folder to backup")
        if folder:
            self.source_folder.set(folder)

    def browse_dest(self):
        folder = filedialog.askdirectory(title="Choose folder to store")
        if folder:
            self.dest_folder.set(folder)

    def start_backup(self):
        if not self.source_folder.get():
            messagebox.showerror("Error", "Please choose a backup folder!")
            return
        if not self.dest_folder.get():
            messagebox.showerror("Error", "Please choose a destination folder!")
            return

        self.start_button.config(state="disabled")
        self.stop_button.config(state="normal")
        self.progress.start()

        self.engine.start_scheduled(
            self.source_folder.get(),
            self.dest_folder.get(),
            self.backup_interval.get()
        )
        self.hide_window()

    def stop_backup(self):
        self.engine.stop_scheduled()
        self.start_button.config(state="normal")
        self.stop_button.config(state="disabled")
        self.progress.stop()

    def manual_backup_now(self):
        if self.engine.is_running:
            threading.Thread(
                target=self.engine.create_backup,
                args=(self.source_folder.get(), self.dest_folder.get()),
                daemon=True
            ).start()

    # --------------------------------------------------------- Tray icon --

    def hide_window(self):
        self.window.withdraw()
        if self.tray_icon is None:
            self.create_tray_icon()

    def show_window(self):
        self.window.deiconify()
        if self.tray_icon:
            self.tray_icon.stop()
            self.tray_icon = None

    def create_tray_icon(self):
        image = Image.new('RGB', (64, 64), color='#FF6B00')
        dc = ImageDraw.Draw(image)
        dc.ellipse([12, 12, 52, 52], fill='#FFD700')
        dc.ellipse([8, 8, 28, 28], fill='#FF6B00')
        dc.ellipse([36, 8, 56, 28], fill='#FF6B00')
        dc.ellipse([8, 36, 28, 56], fill='#FF6B00')
        dc.ellipse([36, 36, 56, 56], fill='#FF6B00')
        dc.ellipse([20, 24, 26, 30], fill='black')
        dc.ellipse([38, 24, 44, 30], fill='black')
        dc.polygon([(32, 32), (28, 38), (36, 38)], fill='#8B4513')

        menu = (
            item('🦁 Show LionBackup', lambda i, it: self.window.after(0, self.show_window)),
            item('💾 Backup now',       lambda i, it: self.manual_backup_now()),
            item('❌ Exit',             lambda i, it: self.quit_app()),
        )
        self.tray_icon = pystray.Icon("lionbackup", image, "LionBackup", menu)
        threading.Thread(target=self.tray_icon.run, daemon=True).start()

    def quit_app(self):
        self.engine.stop_scheduled()
        if self.tray_icon:
            try:
                self.tray_icon.stop()
            except Exception:
                pass
        try:
            self.window.quit()
            self.window.destroy()
        except Exception:
            pass
        import os
        os._exit(0)

    def run(self):
        self.window.mainloop()


if __name__ == "__main__":
    app = LionBackupApp()
    app.run()
