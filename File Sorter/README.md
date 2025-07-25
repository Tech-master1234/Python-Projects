# File Sorter

This is a simple file sorting application that helps you organize files in a specified directory. It offers two sorting methods: by predefined categories or by file extension.

## Features

- **Category-based Sorting**: Sorts files into predefined categories such as 'Images', 'Documents', 'Audio', etc.
- **Extension-based Sorting**: Sorts files into folders named after their respective file extensions (e.g., '.pdf', '.jpg').
- **Graphical User Interface (GUI)**: A user-friendly interface built with Tkinter for easy interaction.
- **Command-Line Interface (CLI)**: Supports sorting directly from the command line for automation or quick use.
- **Fault Tolerance**: Includes error handling for file operations (e.g., permission errors, files in use) to ensure robustness.
- **Executable**: Can be bundled into a standalone executable for easy distribution and use without a Python environment.

## How to Use

### Using the Graphical User Interface (GUI)

1.  **Run the application**: If you have the executable, simply run `file_sorter.exe` from the `dist` folder. If you are running from source, execute `python main.py`.
2.  **Select Directory**: Click the "Browse" button to choose the directory you want to sort.
3.  **Choose Sorting Method**: Select either "Sort by Category" or "Sort by Extension" using the radio buttons.
4.  **Start Sorting**: Click the "Start Sorting" button to begin the process.
5.  **View Results**: A message box will appear showing the summary of sorted files or any errors encountered.

### Using the Command-Line Interface (CLI)

To use the CLI, run `python file_sorter.py` followed by the directory path:

```bash
python file_sorter.py "C:\Users\YourUser\Downloads"
```

The script will then prompt you to choose a sorting method (1 for category, 2 for extension).

## Building the Executable

To create a standalone executable (`file_sorter.exe`) using PyInstaller, follow these steps:

1.  **Install PyInstaller**: If you haven't already, install PyInstaller:
    ```bash
    pip install pyinstaller
    ```

2.  **Navigate to the project directory**: Open your terminal or command prompt and navigate to the root directory of the File Sorter project.

3.  **Build the executable**: Run the following command:
    ```bash
    pyinstaller --onefile --windowed --name file_sorter --add-data "favicon.ico;." main.py
    ```

    -   `--onefile`: Bundles everything into a single executable file.
    -   `--windowed`: Prevents a console window from appearing when the application runs.
    -   `--name file_sorter`: Sets the name of the executable to `file_sorter`.
    -   `--add-data "favicon.ico;."`: Includes the `favicon.ico` file in the executable, making it available at runtime for the Tkinter window.

After the build process completes, you will find the `file_sorter.exe` in the `dist` directory.