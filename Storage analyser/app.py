import os
from flask import Flask, render_template, request, redirect, url_for, flash
from collections import defaultdict

app = Flask(__name__)
app.secret_key = 'storage-secret'  # Needed for flash messages

BASE_DIR = os.path.abspath(".")
TOP_N = 50

def get_readable_size(size_in_bytes):
    for unit in ['B', 'KB', 'MB', 'GB', 'TB']:
        if size_in_bytes < 1024:
            return f"{size_in_bytes:.2f} {unit}"
        size_in_bytes /= 1024
    return f"{size_in_bytes:.2f} PB"

def analyze_storage(root_dir):
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

    largest_files.sort(key=lambda x: x[1], reverse=True)
    return {
        "folder_sizes": folder_sizes,
        "ext_sizes": ext_sizes,
        "largest_files": largest_files[:TOP_N]
    }

@app.route("/")
def index():
    data = analyze_storage(BASE_DIR)
    return render_template("index.html",
                           folder_sizes=data["folder_sizes"],
                           ext_sizes=data["ext_sizes"],
                           largest_files=data["largest_files"],
                           get_readable_size=get_readable_size)

@app.route("/delete", methods=["POST"])
def delete_file():
    filepath = request.form.get("filepath")
    if filepath and os.path.exists(filepath):
        try:
            os.remove(filepath)
            flash(f"✅ Deleted: {filepath}", "success")
        except Exception as e:
            flash(f"❌ Error deleting file: {str(e)}", "danger")
    else:
        flash("⚠️ File does not exist or path was invalid.", "warning")
    return redirect(url_for("index"))

if __name__ == "__main__":
    app.run(debug=True)
