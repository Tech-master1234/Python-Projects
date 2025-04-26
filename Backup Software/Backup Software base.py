import os
import time

# NAS source directory
NAS_SOURCE = r"\\192.168.1.41\student"

# Local backup directory
BACKUP_DIR = r"D:\Student backup"

def backup_with_robocopy(src, dest):
    """Use robocopy to copy files efficiently without deleting old backups."""
    command = f'robocopy "{src}" "{dest}" /E /Z /R:3 /W:5 /NP'
    os.system(command)  # Execute the command

while True:
    print(f"Starting backup from {NAS_SOURCE} to {BACKUP_DIR} using Robocopy...")
    backup_with_robocopy(NAS_SOURCE, BACKUP_DIR)


