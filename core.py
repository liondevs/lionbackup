"""
LionBackup - Core backup logic
Shared between GUI and CLI versions
Author: liondevs (Martin Kostadinov)
"""

import os
import zipfile
import time
import threading
from datetime import datetime


class BackupEngine:
    """Core backup engine - UI agnostic"""

    def __init__(self):
        self.is_running = False
        self.backup_thread = None
        self._status_callback = None
        self._error_callback = None

    def set_status_callback(self, callback):
        """Called with (message: str, level: str) on status change"""
        self._status_callback = callback

    def set_error_callback(self, callback):
        """Called with (message: str) on error"""
        self._error_callback = callback

    def _emit_status(self, message, level="info"):
        if self._status_callback:
            self._status_callback(message, level)

    def _emit_error(self, message):
        if self._error_callback:
            self._error_callback(message)

    def get_next_backup_name(self, dest: str, base_name: str) -> str:
        """Returns next available backup zip filename"""
        zip_path = os.path.join(dest, f"{base_name}.zip")
        if not os.path.exists(zip_path):
            return f"{base_name}.zip"

        counter = 2
        while True:
            zip_path = os.path.join(dest, f"{base_name}-{counter}.zip")
            if not os.path.exists(zip_path):
                return f"{base_name}-{counter}.zip"
            counter += 1

    def create_backup(self, source: str, dest: str) -> bool:
        """
        Creates a zip backup of source folder into dest.
        Returns True on success, False on failure.
        """
        try:
            if not os.path.exists(source):
                self._emit_error(f"Source folder does not exist: {source}")
                return False

            if not os.path.exists(dest):
                os.makedirs(dest)
                self._emit_status(f"Created destination folder: {dest}", "info")

            timestamp = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
            folder_name = os.path.basename(source)
            base_name = f"lionbackup_{folder_name}_{timestamp}"

            zip_filename = self.get_next_backup_name(dest, base_name)
            zip_path = os.path.join(dest, zip_filename)

            self._emit_status(f"Creating backup: {zip_filename}", "info")

            file_count = 0
            with zipfile.ZipFile(zip_path, 'w', zipfile.ZIP_DEFLATED) as zipf:
                for root, dirs, files in os.walk(source):
                    for file in files:
                        file_path = os.path.join(root, file)
                        arcname = os.path.relpath(file_path, source)
                        zipf.write(file_path, arcname)
                        file_count += 1

            size_kb = os.path.getsize(zip_path) / 1024
            self._emit_status(
                f"Backup done: {zip_filename} ({file_count} files, {size_kb:.1f} KB)",
                "success"
            )
            return True

        except Exception as e:
            self._emit_error(f"Backup failed: {str(e)}")
            return False

    def _backup_loop(self, source: str, dest: str, interval_minutes: int):
        """Internal loop for scheduled backups"""
        while self.is_running:
            self.create_backup(source, dest)

            interval_seconds = interval_minutes * 60
            self._emit_status(
                f"Next backup in {interval_minutes} minute(s)...",
                "info"
            )

            for _ in range(interval_seconds):
                if not self.is_running:
                    break
                time.sleep(1)

    def start_scheduled(self, source: str, dest: str, interval_minutes: int):
        """Start automatic scheduled backups in background thread"""
        if self.is_running:
            self._emit_status("Backup already running", "warning")
            return

        if not source or not dest:
            self._emit_error("Source and destination folders are required")
            return

        self.is_running = True
        self.backup_thread = threading.Thread(
            target=self._backup_loop,
            args=(source, dest, interval_minutes),
            daemon=True
        )
        self.backup_thread.start()
        self._emit_status(
            f"Scheduled backup started (every {interval_minutes} min)", "success"
        )

    def stop_scheduled(self):
        """Stop the scheduled backup loop"""
        if not self.is_running:
            return
        self.is_running = False
        self._emit_status("Backup stopped", "warning")

    def wait_for_completion(self):
        """Block until the backup thread finishes (for CLI use)"""
        if self.backup_thread and self.backup_thread.is_alive():
            self.backup_thread.join()
