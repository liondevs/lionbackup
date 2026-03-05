import tkinter as tk
from tkinter import filedialog, messagebox, ttk
import os
import shutil
import zipfile
from datetime import datetime
import threading
import time
from PIL import Image, ImageDraw
import pystray
from pystray import MenuItem as item
import sys

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
        self.is_running = False
        self.backup_thread = None
        self.tray_icon = None
        
        self.create_gui()
        
    def create_gui(self):
        # Header
        title = tk.Label(self.window, text="🦁 LionBackup", 
                        font=("Arial", 18, "bold"),
                        fg="#FF6B00")
        title.pack(pady=10)
        
        subtitle = tk.Label(self.window, text="Auto Files Backup", 
                           font=("Arial", 9),
                           fg="gray")
        subtitle.pack()
        
        # Frame for source folder
        source_frame = tk.Frame(self.window)
        source_frame.pack(pady=10, padx=20, fill="x")
        
        tk.Label(source_frame, text="Folder to backup:", 
                font=("Arial", 10)).pack(anchor="w")
        
        source_entry_frame = tk.Frame(source_frame)
        source_entry_frame.pack(fill="x")
        
        tk.Entry(source_entry_frame, textvariable=self.source_folder, 
                width=40).pack(side="left", fill="x", expand=True)
        tk.Button(source_entry_frame, text="Choose", 
                 command=self.browse_source).pack(side="left", padx=5)
        
        # Frame for destination folder
        dest_frame = tk.Frame(self.window)
        dest_frame.pack(pady=10, padx=20, fill="x")
        
        tk.Label(dest_frame, text="Where to save:", 
                font=("Arial", 10)).pack(anchor="w")
        
        dest_entry_frame = tk.Frame(dest_frame)
        dest_entry_frame.pack(fill="x")
        
        tk.Entry(dest_entry_frame, textvariable=self.dest_folder, 
                width=40).pack(side="left", fill="x", expand=True)
        tk.Button(dest_entry_frame, text="Choose", 
                 command=self.browse_dest).pack(side="left", padx=5)
        
        # Frame for interval
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
        
        self.start_button = tk.Button(button_frame, text="▶ Start", 
                                      command=self.start_backup,
                                      bg="#FF6B00", fg="white", 
                                      font=("Arial", 12, "bold"),
                                      width=12)
        self.start_button.pack(side="left", padx=5)
        
        self.stop_button = tk.Button(button_frame, text="⏸ Stop", 
                                     command=self.stop_backup,
                                     bg="#f44336", fg="white", 
                                     font=("Arial", 12, "bold"),
                                     width=12, state="disabled")
        self.stop_button.pack(side="left", padx=5)
        
        # Status
        self.status_label = tk.Label(self.window, 
                                     text="Status: Disabled", 
                                     font=("Arial", 10),
                                     fg="gray")
        self.status_label.pack(pady=10)
        
        # Progress bar
        self.progress = ttk.Progressbar(self.window, mode='indeterminate')
        self.progress.pack(pady=5, padx=20, fill="x")
        
        # Spacer
        spacer = tk.Frame(self.window, height=20)
        spacer.pack(fill="both", expand=True)
        
        # Footer
        footer_frame = tk.Frame(self.window, bg="#2c3e50", height=35)
        footer_frame.pack(side="bottom", fill="x")
        footer_frame.pack_propagate(False)
        
        footer_label = tk.Label(footer_frame, 
                               text="Author: liondevs (Martin Kostadinov)", 
                               font=("Arial", 9, "bold"),
                               bg="#2c3e50",
                               fg="#ecf0f1")
        footer_label.pack(expand=True)
        
    def browse_source(self):
        folder = filedialog.askdirectory(title="Choose folder to backup")
        if folder:
            self.source_folder.set(folder)
            
    def browse_dest(self):
        folder = filedialog.askdirectory(title="Choose folder to store")
        if folder:
            self.dest_folder.set(folder)
            
    def get_next_backup_name(self, base_name):
        """Finds next available backup name"""
        dest = self.dest_folder.get()
        
        # Check if original name exists
        zip_path = os.path.join(dest, f"{base_name}.zip")
        if not os.path.exists(zip_path):
            return f"{base_name}.zip"
        
        # Searching next number
        counter = 2
        while True:
            zip_path = os.path.join(dest, f"{base_name}-{counter}.zip")
            if not os.path.exists(zip_path):
                return f"{base_name}-{counter}.zip"
            counter += 1
            
    def create_backup(self):
        """Creates zip archive and choosed folder"""
        try:
            source = self.source_folder.get()
            dest = self.dest_folder.get()
            
            if not os.path.exists(source):
                self.update_status("Error: Choosed backup folder does not exist!", "red")
                return
                
            if not os.path.exists(dest):
                os.makedirs(dest)
            
            # Generate backup name
            timestamp = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
            folder_name = os.path.basename(source)
            base_name = f"lionbackup_{folder_name}_{timestamp}"
            
            zip_filename = self.get_next_backup_name(base_name)
            zip_path = os.path.join(dest, zip_filename)
            
            self.update_status(f"Creating backup: {zip_filename}", "blue")
            
            # Creating ZIP archive
            with zipfile.ZipFile(zip_path, 'w', zipfile.ZIP_DEFLATED) as zipf:
                for root, dirs, files in os.walk(source):
                    for file in files:
                        file_path = os.path.join(root, file)
                        arcname = os.path.relpath(file_path, source)
                        zipf.write(file_path, arcname)
            
            self.update_status(f"✓ Backup done: {zip_filename}", "green")
            
        except Exception as e:
            self.update_status(f"Error: {str(e)}", "red")
            
    def update_status(self, message, color="black"):
        """Update status label"""
        try:
            if self.status_label.winfo_exists():
                self.status_label.config(text=f"Status: {message}", fg=color)
        except:
            pass
            
    def backup_loop(self):
        """Periodic backup creating"""
        while self.is_running:
            self.create_backup()
            
            # Изчакваме интервала
            interval_seconds = self.backup_interval.get() * 60
            for _ in range(interval_seconds):
                if not self.is_running:
                    break
                time.sleep(1)
                
    def start_backup(self):
        """Starting the backup process"""
        if not self.source_folder.get():
            messagebox.showerror("Error", "Please choose backup folder!")
            return
            
        if not self.dest_folder.get():
            messagebox.showerror("Error", "Please choose folder for saving!")
            return
            
        self.is_running = True
        self.start_button.config(state="disabled")
        self.stop_button.config(state="normal")
        self.progress.start()
        
        # Starting backup loop
        self.backup_thread = threading.Thread(target=self.backup_loop, daemon=True)
        self.backup_thread.start()
        
        # Minimizing to tray
        self.hide_window()
        
    def stop_backup(self):
        """Stop the backup process"""
        self.is_running = False
        self.start_button.config(state="normal")
        self.stop_button.config(state="disabled")
        self.progress.stop()
        self.update_status("Stopped", "orange")
        
    def hide_window(self):
        """Hides window and shows tray icon"""
        self.window.withdraw()
        if self.tray_icon is None:
            self.create_tray_icon()
            
    def show_window(self):
        """Shows the window"""
        self.window.deiconify()
        if self.tray_icon:
            self.tray_icon.stop()
            self.tray_icon = None
            
    def create_tray_icon(self):
        """Creates system tray icon"""
        # Creating lion icon (orange color)
        image = Image.new('RGB', (64, 64), color='#FF6B00')
        dc = ImageDraw.Draw(image)
        
        # Рисуваме опростен лъв
        # Глава
        dc.ellipse([12, 12, 52, 52], fill='#FFD700')
        # Грива
        dc.ellipse([8, 8, 28, 28], fill='#FF6B00')
        dc.ellipse([36, 8, 56, 28], fill='#FF6B00')
        dc.ellipse([8, 36, 28, 56], fill='#FF6B00')
        dc.ellipse([36, 36, 56, 56], fill='#FF6B00')
        # Очи
        dc.ellipse([20, 24, 26, 30], fill='black')
        dc.ellipse([38, 24, 44, 30], fill='black')
        # Нос
        dc.polygon([(32, 32), (28, 38), (36, 38)], fill='#8B4513')
        
        menu = (
            item('🦁 Show LionBackup', self.show_window_action),
            item('💾 Create backup now', self.manual_backup),
            item('❌ Exit', self.quit_app)
        )
        
        self.tray_icon = pystray.Icon("lionbackup", image, "LionBackup - liondevs", menu)
        
        # Start the icon in other thread
        threading.Thread(target=self.tray_icon.run, daemon=True).start()
        
    def show_window_action(self, icon=None, item=None):
        """Shows the window from tray"""
        self.window.after(0, self.show_window)
        
    def manual_backup(self, icon=None, item=None):
        """Create backup manually"""
        if self.is_running:
            threading.Thread(target=self.create_backup, daemon=True).start()
            
    def quit_app(self, icon=None, item=None):
        """Closes the program completely"""
        self.is_running = False
        
        # Stops the tray icon
        if self.tray_icon:
            try:
                self.tray_icon.stop()
            except:
                pass
        
        # Closing the window
        try:
            self.window.quit()
            self.window.destroy()
        except:
            pass
        
        # Absolute close
        os._exit(0)
        
    def run(self):
        """Starts the application"""
        self.window.mainloop()

if __name__ == "__main__":
    app = LionBackupApp()
    app.run()