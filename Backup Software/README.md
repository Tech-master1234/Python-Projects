# Backup and Sync Tool

This is a web-based backup and synchronization tool built with Flask.

## Features

- User authentication and management (admin/user roles)
- Create, start, stop, and delete backup/sync tasks
- Supports 'Backup', 'Sync', and 'Bi-Sync' methods using Robocopy
- Scheduled tasks (interval or specific time)
- Admin panel for user and task management
- Theme toggling (light/dark mode)

## Setup and Installation

1.  **Clone the repository (if applicable):**

    ```bash
    git clone <repository_url>
    cd "Backup Software"
    ```

2.  **Create a virtual environment (recommended):**

    ```bash
    python -m venv venv
    ```

3.  **Activate the virtual environment:**

    *   **Windows:**

        ```bash
        .\venv\Scripts\activate
        ```

    *   **macOS/Linux:**

        ```bash
        source venv/bin/activate
        ```

4.  **Install dependencies:**

    ```bash
    pip install -r requirements.txt
    ```

## Running the Application

To run the application in a production-ready manner using Waitress:

```bash
python BeSync.py
```

The application will be accessible at `http://127.0.0.1:5000` by default, or `http://0.0.0.0:5000` if multi-device access is enabled in the settings.

## Initial Admin Credentials

Upon the first run, a default admin user will be created:

-   **Username:** `admin`
-   **Password:** `admin`

It is highly recommended to change these credentials immediately after the first login.

## Project Structure

```
Backup Software/
├───Backup Software base.py  # (Optional) Separate script for direct Robocopy backup
├───BeSync.py                # Main Flask application
├───Setup.py                 # (If exists) Setup script for the application
├───sync.ico                 # Application icon
├───instance/                # Contains SQLite database (users.db)
│   └───users.db
├───templates/               # HTML templates for the web interface
│   ├───admin_settings.html
│   ├───admin_users.html
│   ├───all_tasks.html
│   ├───base.html
│   ├───change_credentials.html
│   ├───index.html
│   ├───login.html
│   └───settings.html
├───requirements.txt         # Python dependencies
└───README.md                # Project README
```