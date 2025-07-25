import tkinter as tk
from tkinter import filedialog, messagebox
from file_sorter import sort_by_category, sort_by_extension

def select_directory():
    directory = filedialog.askdirectory()
    if directory:
        entry_directory.delete(0, tk.END)
        entry_directory.insert(0, directory)

def start_sorting():
    directory = entry_directory.get()
    if not directory:
        messagebox.showerror("Error", "Please select a directory.")
        return

    sort_choice = var_sort_choice.get()
    errors = []
    summary_message = ""
    if sort_choice == 1:
        errors, summary_message = sort_by_category(directory)
    elif sort_choice == 2:
        errors, summary_message = sort_by_extension(directory)
    else:
        messagebox.showerror("Error", "Please select a sorting method.")
        return

    if errors:
        error_message = "The following errors occurred:\n\n" + "\n".join(errors)
        messagebox.showwarning("Errors", error_message)
    else:
        messagebox.showinfo("Sorting Complete", summary_message)

# --- GUI Setup ---
root = tk.Tk()
root.title("File Sorter")
import sys
import os

def resource_path(relative_path):
    """ Get absolute path to resource, works for dev and for PyInstaller """
    try:
        # PyInstaller creates a temp folder and stores path in _MEIPASS
        base_path = sys._MEIPASS
    except Exception:
        base_path = os.path.abspath(".")

    return os.path.join(base_path, relative_path)

root.iconbitmap(resource_path("favicon.ico"))

# Directory Selection
frame_dir = tk.Frame(root, padx=10, pady=10)
frame_dir.pack()

label_dir = tk.Label(frame_dir, text="Directory:")
label_dir.pack(side=tk.LEFT)

entry_directory = tk.Entry(frame_dir, width=50)
entry_directory.pack(side=tk.LEFT, padx=5)

btn_browse = tk.Button(frame_dir, text="Browse", command=select_directory)
btn_browse.pack(side=tk.LEFT)

# Sorting Options
frame_options = tk.Frame(root, padx=10, pady=5)
frame_options.pack()

var_sort_choice = tk.IntVar()
radio_category = tk.Radiobutton(frame_options, text="Sort by Category", variable=var_sort_choice, value=1)
radio_category.pack(anchor=tk.W)

radio_extension = tk.Radiobutton(frame_options, text="Sort by Extension", variable=var_sort_choice, value=2)
radio_extension.pack(anchor=tk.W)

# Start Button
btn_start = tk.Button(root, text="Start Sorting", command=start_sorting, padx=10, pady=5)
btn_start.pack(pady=10)

root.mainloop()