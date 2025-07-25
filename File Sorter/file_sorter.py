import os
import shutil
import sys
from datetime import datetime
from collections import defaultdict

# Extension to Category Mapping
EXTENSION_MAP = {
    "Audio": ["m4a", "mp3", "ogg", "wav", "wma"],
    "Compressed Folders": ["7z", "gz", "tar", "zip"],
    "Documents": ["csv", "doc", "docx", "rtf", "xml"],
    "Text": ["txt"],
    "Excel" : ["csv","xls", "xlsb", "xlsm", "xlsx"],
    "GIFs": ["gif"],
    "Images": ["jpeg", "jpg", "png", "svg", "tiff", "webp"],
    "Installers": ["msi"],
    "PDFs": ["pdf"],
    "Presentations": ["ppt", "pptx"],
    "Programming": ["c", "cpp", "h", "java", "js", "lua", "php", "py", "ts"],
    "Programs": ["bat", "exe", "lnk"],
    "Templates": ["xlt", "xltx"],
    "Videos": ["avi", "mkv", "mov", "mp4", "wmv"],
    "Websites": ["css", "htm", "html"],
}

# Inverse map: extension -> category
EXT_TO_CAT = {}
for category, exts in EXTENSION_MAP.items():
    for ext in exts:
        EXT_TO_CAT[ext.lower()] = category

# Returns category or "Others"
def get_category(extension):
    return EXT_TO_CAT.get(extension.lower(), "Others")

# Avoid overwriting existing files
def resolve_duplicate(destination_path):
    if not os.path.exists(destination_path):
        return destination_path

    base, ext = os.path.splitext(destination_path)
    counter = 1
    while True:
        new_path = f"{base}_{counter}{ext}"
        if not os.path.exists(new_path):
            return new_path
        counter += 1

# Sorter by category
def sort_by_category(directory):
    errors = []
    if not os.path.isdir(directory):
        errors.append(f"❌ '{directory}' is not a valid directory.")
        return errors

    file_count = defaultdict(int)
    sorted_count = 0

    for item in os.listdir(directory):
        item_path = os.path.join(directory, item)

        if os.path.isdir(item_path):
            continue

        _, ext = os.path.splitext(item)
        ext = ext[1:].lower()

        category = get_category(ext)
        target_dir = os.path.join(directory, category)

        try:
            if not os.path.exists(target_dir):
                os.makedirs(target_dir)
        except OSError as e:
            errors.append(f"Could not create directory {target_dir}: {e}")
            continue

        destination_path = os.path.join(target_dir, item)
        destination_path = resolve_duplicate(destination_path)

        try:
            shutil.move(item_path, destination_path)
            file_count[category] += 1
            sorted_count += 1
        except OSError as e:
            errors.append(f"Could not move file {item_path}: {e}")

    summary = [f"✅ Sorted {sorted_count} files into {len(file_count)} categories:"]
    for cat, count in file_count.items():
        summary.append(f"  • {cat}: {count} file(s)")
    
    return errors, "\n".join(summary)

# Sorter by extension
def sort_by_extension(directory):
    errors = []
    if not os.path.isdir(directory):
        errors.append(f"❌ '{directory}' is not a valid directory.")
        return errors

    file_count = defaultdict(int)
    sorted_count = 0

    for item in os.listdir(directory):
        item_path = os.path.join(directory, item)

        if os.path.isdir(item_path):
            continue

        _, ext = os.path.splitext(item)
        ext = ext[1:].lower()

        if not ext:
            continue

        target_dir = os.path.join(directory, ext)

        try:
            if not os.path.exists(target_dir):
                os.makedirs(target_dir)
        except OSError as e:
            errors.append(f"Could not create directory {target_dir}: {e}")
            continue

        destination_path = os.path.join(target_dir, item)
        destination_path = resolve_duplicate(destination_path)

        try:
            shutil.move(item_path, destination_path)
            file_count[ext] += 1
            sorted_count += 1
        except OSError as e:
            errors.append(f"Could not move file {item_path}: {e}")

    summary = [f"✅ Sorted {sorted_count} files into {len(file_count)} folders based on extension:"]
    for ext, count in file_count.items():
        summary.append(f"  • {ext}: {count} file(s)")

    return errors, "\n".join(summary)

# Entry point
if __name__ == "__main__":
    main()
