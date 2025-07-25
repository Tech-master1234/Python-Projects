
import os
import psutil
from collections import defaultdict

CATEGORY_MAP = {
    "Videos": [".mp4", ".mkv", ".avi", ".wmv", ".mov"],
    "Audio": [".mp3", ".wav", ".ogg", ".flac"],
    "Documents": [".pdf", ".docx", ".xlsx", ".pptx", ".txt"],
    "Compressed": [".zip", ".rar", ".7z", ".tar"],
    "Images": [".jpg", ".png", ".gif", ".svg", ".tiff"],
    "Installation": [".exe", ".msi"],
    "Apps": [".lnk"],
}

SYSTEM_DIRS = ["C:\\Windows", "C:\\System Volume Information"]
APPS_DIRS = ["C:\\Program Files", "C:\\Program Files (x86)"]

def get_category(extension, path):
    for category, ext_list in CATEGORY_MAP.items():
        if extension.lower() in ext_list:
            return category
    if any(path.startswith(folder) for folder in SYSTEM_DIRS):
        return "System"
    if any(path.startswith(folder) for folder in APPS_DIRS):
        return "Apps"
    return "Other"

def analyze_storage(root_dir="C:\\"):
    usage = psutil.disk_usage(root_dir)
    data = defaultdict(int)

    for dirpath, _, filenames in os.walk(root_dir):
        for file in filenames:
            try:
                full_path = os.path.join(dirpath, file)
                if not os.path.isfile(full_path):
                    continue
                ext = os.path.splitext(file)[1]
                category = get_category(ext, full_path)
                size = os.path.getsize(full_path)
                data[category] += size
            except:
                continue

    return {
        "total": usage.total,
        "used": usage.used,
        "free": usage.free,
        "categories": {k: v for k, v in data.items()}
    }
