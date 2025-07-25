import os
import argparse
from collections import defaultdict

def get_readable_size(size_in_bytes):
    for unit in ['B', 'KB', 'MB', 'GB', 'TB']:
        if size_in_bytes < 1024:
            return f"{size_in_bytes:.2f} {unit}"
        size_in_bytes /= 1024
    return f"{size_in_bytes:.2f} PB"

def analyze_storage(root_dir, top_n=10):
    ext_sizes = defaultdict(int)
    folder_sizes = defaultdict(int)
    largest_files = []

    for dirpath, _, filenames in os.walk(root_dir):
        for fname in filenames:
            fpath = os.path.join(dirpath, fname)
            try:
                size = os.path.getsize(fpath)
            except (FileNotFoundError, PermissionError):
                continue

            ext = os.path.splitext(fname)[1].lower() or 'NO_EXT'
            ext_sizes[ext] += size
            folder_sizes[dirpath] += size

            largest_files.append((fpath, size))

    # Sort and format
    largest_files.sort(key=lambda x: x[1], reverse=True)

    print("\n📂 Folder Size Summary:")
    for folder, size in sorted(folder_sizes.items(), key=lambda x: x[1], reverse=True):
        print(f"{folder:<60} {get_readable_size(size)}")

    print("\n📄 File Type Summary:")
    for ext, size in sorted(ext_sizes.items(), key=lambda x: x[1], reverse=True):
        print(f"{ext:<10} {get_readable_size(size)}")

    print(f"\n🔝 Top {top_n} Largest Files:")
    for fpath, size in largest_files[:top_n]:
        print(f"{get_readable_size(size):>10} - {fpath}")

# CLI
def main():
    parser = argparse.ArgumentParser(description="📊 Storage Analyzer")
    parser.add_argument("directory", help="Directory to analyze")
    parser.add_argument("--top", type=int, default=10, help="Show top N largest files")
    args = parser.parse_args()

    if not os.path.isdir(args.directory):
        print("❌ Provided path is not a valid directory.")
        return

    analyze_storage(args.directory, args.top)

if __name__ == "__main__":
    main()
