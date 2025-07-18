import os
import shutil
import ctypes
import sys
import winshell
from win32com.client import Dispatch
import tkinter as tk
from tkinter import ttk, filedialog, messagebox
import subprocess
import winreg

def get_file_version(file_path):
    """Gets the file version of a given file."""
    from win32api import GetFileVersionInfo, LOWORD, HIWORD
    try:
        info = GetFileVersionInfo(file_path, '\\')
        ms = info['FileVersionMS']
        ls = info['FileVersionLS']
        return f"{HIWORD(ms)}.{LOWORD(ms)}.{HIWORD(ls)}.{LOWORD(ls)}"
    except Exception:
        return "1.0.0.0"  # Default version

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
        # Fallback for Python 2
        ctypes.windll.shell32.ShellExecuteW(
            None, u"runas", unicode(sys.executable), unicode(" ".join(sys.argv)), None, 1
        )

def install(install_dir, add_to_startup):
    """Performs the installation."""
    try:
        APP_NAME = "BeSync"
        PUBLISHER = "Tech-master1234"
        
        # Define paths
        exe_source = resource_path("BeSync.exe")
        uninstaller_source = resource_path("uninstaller.exe")
        
        exe_destination = os.path.join(install_dir, f"{APP_NAME}.exe")
        uninstaller_destination = os.path.join(install_dir, "uninstaller.exe")
        icon_path = exe_destination # Icon is embedded in the exe

        # 1. Create installation directory
        if not os.path.exists(install_dir):
            os.makedirs(install_dir)

        # 2. Copy executable and uninstaller
        shutil.copy(exe_source, exe_destination)
        shutil.copy(uninstaller_source, uninstaller_destination)

        # 3. Create Registry entries for "Apps & Features"
        version = get_file_version(exe_destination)
        uninstall_string = f'"{uninstaller_destination}"'
        
        registry_path = rf"SOFTWARE\Microsoft\Windows\CurrentVersion\Uninstall\{APP_NAME}"
        with winreg.CreateKey(winreg.HKEY_LOCAL_MACHINE, registry_path) as key:
            winreg.SetValueEx(key, "DisplayName", 0, winreg.REG_SZ, APP_NAME)
            winreg.SetValueEx(key, "DisplayVersion", 0, winreg.REG_SZ, version)
            winreg.SetValueEx(key, "Publisher", 0, winreg.REG_SZ, PUBLISHER)
            winreg.SetValueEx(key, "InstallLocation", 0, winreg.REG_SZ, install_dir)
            winreg.SetValueEx(key, "DisplayIcon", 0, winreg.REG_SZ, exe_destination)
            winreg.SetValueEx(key, "UninstallString", 0, winreg.REG_SZ, uninstall_string)
            winreg.SetValueEx(key, "NoModify", 0, winreg.REG_DWORD, 1)
            winreg.SetValueEx(key, "NoRepair", 0, winreg.REG_DWORD, 1)

        # 4. Create Start Menu shortcuts
        start_menu_path = os.path.join(winshell.programs(), APP_NAME)
        if not os.path.exists(start_menu_path):
            os.makedirs(start_menu_path)

        shell = Dispatch('WScript.Shell')

        # Shortcut to the application
        shortcut_path = os.path.join(start_menu_path, f"{APP_NAME}.lnk")
        shortcut = shell.CreateShortcut(shortcut_path)
        shortcut.TargetPath = exe_destination
        shortcut.IconLocation = icon_path
        shortcut.WorkingDirectory = install_dir
        shortcut.Save()

        # Shortcut to the uninstaller
        uninstaller_shortcut_path = os.path.join(start_menu_path, "Uninstall.lnk")
        shortcut = shell.CreateShortcut(uninstaller_shortcut_path)
        shortcut.TargetPath = uninstaller_destination
        shortcut.IconLocation = uninstaller_destination # Uninstaller has its own icon
        shortcut.Save()

        # 5. Add to startup if requested
        if add_to_startup:
            startup_folder = winshell.startup()
            startup_shortcut_path = os.path.join(startup_folder, f"{APP_NAME}.lnk")
            # Create a VBScript to run the app silently
            vbs_path = os.path.join(install_dir, "run_silent.vbs")
            vbs_content = f'Set WshShell = CreateObject("WScript.Shell")\nWshShell.Run """{exe_destination}""", 0, False\nSet WshShell = Nothing'
            with open(vbs_path, "w") as vbs_file:
                vbs_file.write(vbs_content)

            shell = Dispatch('WScript.Shell')
            shortcut = shell.CreateShortcut(startup_shortcut_path)
            shortcut.TargetPath = vbs_path
            shortcut.IconLocation = icon_path
            shortcut.WorkingDirectory = install_dir
            shortcut.Save()

        # 6. Start the application
        subprocess.Popen([exe_destination])
        import webbrowser
        webbrowser.open("http://localhost:5010")

        messagebox.showinfo("Success", f"{APP_NAME} has been installed successfully.")
        return True
    except Exception as e:
        messagebox.showerror("Error", f"An error occurred during setup: {e}")
        # Clean up on failure
        try:
            if os.path.exists(install_dir):
                shutil.rmtree(install_dir)
            # Add registry cleanup here if needed
        except Exception as cleanup_e:
            messagebox.showerror("Cleanup Error", f"Failed to clean up after installation error: {cleanup_e}")
        return False


class InstallerApp(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("BeSync Installer")
        self.iconbitmap(resource_path("sync.ico"))
        self.geometry("500x400")

        # --- UI Elements ---
        # Installation Path
        # Configure grid weights for resizing
        self.grid_columnconfigure(0, weight=1)
        self.grid_columnconfigure(1, weight=1)
        self.grid_rowconfigure(0, weight=0)
        self.grid_rowconfigure(1, weight=0)
        self.grid_rowconfigure(2, weight=0)
        self.grid_rowconfigure(3, weight=0) # Terms label
        self.grid_rowconfigure(4, weight=1) # Terms text area
        self.grid_rowconfigure(5, weight=0)

        # Installation Path
        self.path_label = ttk.Label(self, text="Installation Folder:")
        self.path_label.grid(row=0, column=0, columnspan=2, pady=5, sticky="w", padx=10)
        self.install_path = tk.StringVar(value=os.path.join(os.environ["ProgramFiles"], "BeSync"))
        self.path_entry = ttk.Entry(self, textvariable=self.install_path, width=50)
        self.path_entry.grid(row=1, column=0, pady=5, padx=10, sticky="ew")
        self.browse_button = ttk.Button(self, text="Browse", command=self.browse_folder)
        self.browse_button.grid(row=1, column=1, pady=5, padx=10, sticky="e")

        # Add to Startup
        self.add_to_startup = tk.BooleanVar(value=True)
        self.startup_check = ttk.Checkbutton(self, text="Add to startup", variable=self.add_to_startup)
        self.startup_check.grid(row=2, column=0, columnspan=2, pady=10, sticky="w", padx=10)

        # Terms and Conditions
        self.terms_label = ttk.Label(self, text="Terms and Conditions:")
        self.terms_label.grid(row=3, column=0, columnspan=2, pady=5, sticky="w", padx=10)
        self.terms_text = tk.Text(self, height=10, width=60)
        self.terms_text.insert(tk.END, "This is a placeholder for your terms and conditions.")
        self.terms_text.config(state=tk.DISABLED)
        self.terms_text.grid(row=4, column=0, columnspan=2, pady=5, padx=10, sticky="nsew")

        # Install Button
        self.install_button = ttk.Button(self, text="Install", command=self.start_installation)
        self.install_button.grid(row=5, column=0, columnspan=2, pady=20)

    def browse_folder(self):
        folder = filedialog.askdirectory()
        if folder:
            self.install_path.set(folder)

    def start_installation(self):
        install_dir = self.install_path.get()
        add_to_startup = self.add_to_startup.get()

        if not install_dir:
            messagebox.showwarning("Warning", "Please select an installation directory.")
            return

        if messagebox.askyesno("Confirm", f"Install BeSync to {install_dir}?"):
            if install(install_dir, add_to_startup):
                self.destroy()

# --- Main Execution ---
if __name__ == "__main__":
    if not is_admin():
        print("This setup requires administrative privileges. Attempting to re-run as admin...")
        run_as_admin()
        sys.exit()
    else:
        app = InstallerApp()
        app.mainloop()