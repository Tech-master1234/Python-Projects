import os
import shutil
import getpass
import winshell
from win32com.client import Dispatch

# Get current username
current_user = getpass.getuser()

# Define BeSync folder path
besync_folder = os.path.join("C:\\Users", current_user, "BeSync")

# Define paths inside BeSync folder
exe_source = os.path.join(os.getcwd(), "BeSync.exe")  # Assuming exe is in the current dir
exe_destination = os.path.join(besync_folder, "BeSync.exe")  # Move exe to BeSync folder
vbs_path = os.path.join(besync_folder, "run_backup.vbs")  # Store VBS inside BeSync
startup_folder = winshell.startup()  # Get Startup folder path
shortcut_path = os.path.join(startup_folder, "Backup Software.lnk")  # Shortcut path
icon_path = os.path.join(os.getcwd(), "sync.ico")  # Icon file

# Ensure BeSync folder exists
if not os.path.exists(besync_folder):
    os.makedirs(besync_folder)
    print(f"Created folder: {besync_folder}")

# Move EXE to the BeSync folder
if not os.path.exists(exe_destination):
    shutil.copy(exe_source, exe_destination)
    print(f"Copied BeSync.exe to {exe_destination}")

# Create VBS script to run the EXE silently
vbs_content = f'''Set WshShell = CreateObject("WScript.Shell")
WshShell.Run """{exe_destination}""", 0, False
Set WshShell = Nothing
'''
with open(vbs_path, "w") as vbs_file:
    vbs_file.write(vbs_content)
print(f"Created VBS script at {vbs_path}")

# Create a shortcut in the Startup folder
shell = Dispatch('WScript.Shell')
shortcut = shell.CreateShortcut(shortcut_path)
shortcut.TargetPath = vbs_path  # Shortcut points to the VBS script
shortcut.IconLocation = icon_path  # Set sync.ico as the icon
shortcut.Save()
print(f"Created Startup shortcut: {shortcut_path}")

# Start BeSync.exe after copying for the first time
print("Starting BeSync.exe for the first time...")
os.system(f'start "" "{exe_destination}"')

print("Setup completed successfully! 'Backup Software' will now run at startup.")
