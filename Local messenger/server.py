from flask import Flask, render_template, request, session, redirect, url_for, jsonify,send_from_directory
from flask_socketio import SocketIO, emit
import hashlib, json, os
from datetime import datetime
from werkzeug.utils import secure_filename

app = Flask(__name__)
app.secret_key = 'secret!'
socketio = SocketIO(app, async_mode="threading")


USERS_FILE = 'users.json'
HISTORY_FILE = 'chat_history.json'

# Ensure the users.json file exists and creates admin if not present
def ensure_users_file():
    default_admin = {
        "password_hash": hashlib.sha256("super@user".encode()).hexdigest(),
        "display_name": "Admin",
        "is_admin": True
    }

    # If users.json does not exist, create it with admin user
    if not os.path.exists(USERS_FILE):
        with open(USERS_FILE, 'w') as f:
            users = {"admin": default_admin}
            json.dump(users, f, indent=2)
        return

    # If it exists, ensure 'admin' user is present
    with open(USERS_FILE, 'r+') as f:
        try:
            users = json.load(f)
        except json.JSONDecodeError:
            users = {}

        if "admin" not in users:
            users["admin"] = default_admin
            f.seek(0)
            json.dump(users, f, indent=2)
            f.truncate()  

def load_users():
    ensure_users_file()
    with open(USERS_FILE) as f:
        return json.load(f)

def save_users(users):
    with open(USERS_FILE, 'w') as f:
        json.dump(users, f, indent=2)

def verify_user(username, password):
    users = load_users()
    if username not in users:
        return False
    hashed = hashlib.sha256(password.encode()).hexdigest()
    return users[username]["password_hash"] == hashed

def is_admin(username):
    users = load_users()
    return users.get(username, {}).get("is_admin", False)

def save_message(sender, message):
    history = []
    if os.path.exists(HISTORY_FILE):
        with open(HISTORY_FILE) as f:
            history = json.load(f)
    history.append({
        "sender": sender,
        "message": message,
        "timestamp": datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    })
    with open(HISTORY_FILE, 'w') as f:
        json.dump(history, f, indent=2)

# Route to handle login
@app.route('/', methods=['GET', 'POST'])
def login():
    if 'username' in session:
        return redirect(url_for('chat'))  # If already logged in, redirect to chat

    if request.method == 'POST':
        user = request.form['username']
        pw = request.form['password']
        if verify_user(user, pw):
            session['username'] = user
            return redirect(url_for('chat'))  # Redirect to chat after login
        else:
            return render_template('chat.html', error="Invalid credentials", show_login=True)

    return render_template('chat.html', show_login=True)

# Chat route
@app.route('/chat')
def chat():
    if 'username' not in session:
        return redirect(url_for('login'))  # Redirect to login if not logged in
    return render_template('chat.html', username=session['username'], show_login=False)

@socketio.on('message')
def handle_message(msg):
    user = session.get('username', 'Unknown')
    save_message(user, msg)
    emit('message', {'user': user, 'msg': msg}, broadcast=True)

@socketio.on('connect')
def handle_connect():
    user = session.get('username', 'Guest')
    emit('message', {'user': 'System', 'msg': f'{user} joined the chat'}, broadcast=True)

@socketio.on('disconnect')
def handle_disconnect():
    user = session.get('username', 'Guest')
    emit('message', {'user': 'System', 'msg': f'{user} left the chat'}, broadcast=True)

# Route to add new users (admin only)
@app.route('/add', methods=['GET', 'POST'])
def add_user():
    if 'username' not in session or not is_admin(session['username']):
        return redirect(url_for('login'))  # Redirect if not logged in or not an admin

    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        cpassword = request.form['cpassword']
        display_name = request.form['display_name']

        # Ensure the username does not already exist
        users = load_users()
        if username in users:
            return render_template('add_user.html', error="Username already exists.")
        
        if password == cpassword:
            # Hash the password before saving
            password_hash = hashlib.sha256(password.encode()).hexdigest()

            # Add the new user to the JSON file
            users[username] = {
                "password_hash": password_hash,
                "display_name": display_name,
                "is_admin": False  # New users are not admins by default
            }
            save_users(users)
        else:
            print("Passwords didn't match")
        return redirect(url_for('login'))

    return render_template('add_user.html')

# Ensure that the users.json file exists and creates an admin if needed
ensure_users_file()

UPLOAD_FOLDER = 'uploads'
ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif', 'pdf', 'docx', 'txt', 'zip'}

app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

@app.route('/upload', methods=['POST'])
def upload_file():
    if 'file' not in request.files or 'username' not in session:
        return 'No file', 400
    file = request.files['file']
    if file.filename == '' or not allowed_file(file.filename):
        return 'Invalid file', 400
    filename = secure_filename(file.filename)
    file.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))
    
    # Broadcast file link
    file_url = url_for('uploaded_file', filename=filename)
    sender = session['username']
    socketio.emit('message', {
        'user': sender,
        'msg': f'<a href="{file_url}" target="_blank">📎 {filename}</a>'
    }, broadcast=True)

    return 'File uploaded', 200

@app.route('/uploads/<filename>')
def uploaded_file(filename):
    return send_from_directory(app.config['UPLOAD_FOLDER'], filename)

if __name__ == '__main__':
    socketio.run(app, host='0.0.0.0', port=8010,debug=True)
