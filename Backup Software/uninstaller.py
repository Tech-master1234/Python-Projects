
import os
import shutil
import subprocess
import ctypes
import sys
import tkinter as tk
from tkinter import messagebox
from appdirs import user_data_dir
import winreg
import winshell

def resource_path(relative_path):
    """ Get absolute path to resource, works for dev and for PyInstaller """
    try:
        # PyInstaller creates a temp folder and stores path in _MEIPASS
        base_path = sys._MEIPASS
    except Exception:
        base_path = os.path.abspath(".")

    return os.path.join(base_path, relative_path)

def is_admin():
    """Check if the script is running with administrative privileges."""
    try:
        return ctypes.windll.shell32.IsUserAnAdmin()
    except:
        return False

def run_as_admin():
    """Re-run the script with administrative privileges."""
    if sys.version_info[0] == 3:
        ctypes.windll.shell32.ShellExecuteW(
            None, "runas", sys.executable, " ".join(sys.argv), None, 1
        )
    else:
        ctypes.windll.shell32.ShellExecuteW(
            None, u"runas", unicode(sys.executable), unicode(" ".join(sys.argv)), None, 1
        )

def stop_process(process_name):
    """Stops a running process by name."""
    try:
        subprocess.run(["taskkill", "/F", "/IM", process_name], check=True, capture_output=True)
    except subprocess.CalledProcessError:
        # Process not found, which is fine
        pass

from appdirs import user_data_dir

def uninstall():
    """Performs the uninstallation."""
    try:
        APP_NAME = "BeSync"
        install_dir = os.path.join(os.environ["ProgramFiles"], APP_NAME)
        data_dir = user_data_dir(APP_NAME, "Tech-master1234")

        # 1. Stop the application process
        stop_process(f"{APP_NAME}.exe")

        # 2. Remove Start Menu folder
        start_menu_path = os.path.join(winshell.programs(), APP_NAME)
        if os.path.exists(start_menu_path):
            shutil.rmtree(start_menu_path)

        # 3. Remove startup shortcut
        startup_shortcut = os.path.join(winshell.startup(), f"{APP_NAME}.lnk")
        if os.path.exists(startup_shortcut):
            os.remove(startup_shortcut)

        # 4. Remove Registry key
        registry_path = rf"SOFTWARE\Microsoft\Windows\CurrentVersion\Uninstall\{APP_NAME}"
        try:
            winreg.DeleteKey(winreg.HKEY_LOCAL_MACHINE, registry_path)
        except FileNotFoundError:
            pass # Key not found, which is fine

        # 5. Remove application data directory
        if os.path.exists(data_dir):
            shutil.rmtree(data_dir)

        # 6. Create a batch script to remove the installation directory
        #    after the uninstaller exits.
        batch_content = f'''@echo off
echo Waiting for BeSync uninstaller to close...
timeout /t 2 /nobreak > NUL
echo Deleting remaining files...
rmdir /s /q "{install_dir}"
del "%~f0"
'''
        batch_path = os.path.join(os.environ["TEMP"], "besync_uninstall.bat")
        with open(batch_path, "w") as f:
            f.write(batch_content)

        # Run the batch script in a new process, detached from the current one.
        subprocess.Popen([batch_path], creationflags=subprocess.CREATE_NEW_CONSOLE)

        messagebox.showinfo("Success", f"{APP_NAME} has been successfully uninstalled.")
        return True
    except Exception as e:
        messagebox.showerror("Error", f"An error occurred during uninstallation: {e}")
        return False

class UninstallerApp(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("BeSync Uninstaller")
        self.geometry("400x200")
        self.iconbitmap(resource_path("sync.ico"))

        self.label = tk.Label(self, text="Are you sure you want to uninstall BeSync?")
        self.label.pack(pady=20)

        self.uninstall_button = tk.Button(self, text="Uninstall", command=self.start_uninstallation)
        self.uninstall_button.pack(pady=10)

    def start_uninstallation(self):
        if messagebox.askyesno("Confirm", "This will remove BeSync and all its data. Continue?"):
            if uninstall():
                self.destroy()

if __name__ == "__main__":
    if not is_admin():
        run_as_admin()
        sys.exit()
    else:
        app = UninstallerApp()
        app.mainloop()
