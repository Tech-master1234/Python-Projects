import os
import json
import time
from flask import Flask, render_template, request

CONFIG_FILE = "config.dat"

main = Flask(__name__, template_folder='templates')

# Function to load configuration from file
def load_config():
    if os.path.exists(CONFIG_FILE):
        with open(CONFIG_FILE, "r") as f:
            return json.load(f)
    return {
        "method": "",
        "source": "",
        "destination": "",
        "days": "0",
        "hours": "0",
        "minutes": "0",
        "seconds": "0"
    }

# Function to save configuration to file
def save_config(data):
    with open(CONFIG_FILE, "w") as f:
        json.dump(data, f, indent=4)

@main.route('/', methods=['GET', 'POST'])
def index():
    config = load_config()

    if request.method == 'POST':
        # Get data from form
        config["method"] = request.form.get('option')
        config["source"] = request.form.get('input-path')
        config["destination"] = request.form.get('output-path')
        config["days"] = request.form.get('days')
        config["hours"] = request.form.get('hours')
        config["minutes"] = request.form.get('minutes')
        config["seconds"] = request.form.get('seconds')

        # Save updated configuration
        save_config(config)

    return render_template('index.html', config=config)

def synchronization(source, destination, seconds):
    command = f'robocopy "{source}" "{destination}" /MIR /Z /R:3 /W:5 /NP'
    os.system(command)
    time.sleep(seconds)

def backup(source, destination, seconds):
    command = f'robocopy "{source}" "{destination}" /E /R:3 /W:5 /NP'
    os.system(command)
    time.sleep(seconds)

# Background process that waits for valid input before running
def run_task():
    while True:
        config = load_config()

        # Wait until user enters valid input
        if config["source"] and config["destination"] and config["method"]:
            print(f"Starting {config['method']} process...")

            seconds = int(config["days"]) * 86400 + int(config["hours"]) * 3600 + int(config["minutes"]) * 60 + int(config["seconds"])

            if config["method"] == 'Backup':
                backup(config["source"], config["destination"], seconds)
            elif config["method"] == 'Sync':
                synchronization(config["source"], config["destination"], seconds)
        else:
            print("Waiting for valid input...")  # Debugging info
            time.sleep(5)  # Wait before checking again

# Run background task in a separate thread
import threading
threading.Thread(target=run_task, daemon=True).start()

if __name__ == '__main__':
    main.run(host='0.0.0.0', debug=True)
