import os
import random

# Directory to store the dummy files
output_dir = "test_files"
os.makedirs(output_dir, exist_ok=True)

# Extensions by category
extensions_by_category = {
    "Audio": ["m4a", "mp3", "ogg", "wav", "wma"],
    "Compressed Folders": ["7z", "gz", "tar", "zip"],
    "Documents": ["csv", "doc", "docx", "rtf", "txt", "xls", "xlsb", "xlsm", "xlsx", "xml"],
    "GIFs": ["gif"],
    "Images": ["jpeg", "jpg", "png", "svg", "tiff", "webp"],
    "Installers": ["msi"],
    "PDFs": ["pdf"],
    "Presentations": ["ppt", "pptx"],
    "Programming": ["c", "cpp", "h", "java", "js", "lua", "php", "py", "ts"],
    "Programs": ["bat", "exe", "lnk"],
    "Templates": ["xlt", "xltx"],
    "Videos": ["avi", "mkv", "mov", "mp4", "wmv"],
    "Websites": ["css", "htm", "html"]
}

# Some unknown/unlisted extensions for testing
unlisted_extensions = ["bak", "tmp", "log", "xyz", "dat"]

# Number of dummy files per extension
files_per_extension = 2

# Function to generate dummy files
def generate_dummy_files():
    count = 0
    for category, extensions in extensions_by_category.items():
        for ext in extensions:
            for i in range(files_per_extension):
                filename = f"{category.lower().replace(' ', '_')}_{i+1}.{ext}"
                filepath = os.path.join(output_dir, filename)
                with open(filepath, "w") as f:
                    f.write(f"Dummy content for {filename}\n")
                count += 1

    for ext in unlisted_extensions:
        for i in range(files_per_extension):
            filename = f"unlisted_{i+1}.{ext}"
            filepath = os.path.join(output_dir, filename)
            with open(filepath, "w") as f:
                f.write(f"Unlisted dummy content for {filename}\n")
            count += 1

    print(f"✅ Generated {count} dummy files in '{output_dir}'")

# Run the generator
if __name__ == "__main__":
    generate_dummy_files()
