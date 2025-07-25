from flask import Flask, request, redirect, jsonify, render_template, url_for, flash
import mysql.connector
import hashlib
import base64
from flask_login import LoginManager, UserMixin, login_user, login_required, logout_user, current_user
from werkzeug.security import generate_password_hash, check_password_hash

app = Flask(__name__)
app.config['SECRET_KEY'] = 'your_secret_key' # Replace with a strong secret key

login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'login_new'

# Database Configuration
DB_CONFIG = {
    'host': 'localhost',
    'user': 'root',
    'password': 'root',
    'database': 'url'
}

def get_db_connection():
    return mysql.connector.connect(**DB_CONFIG)

# User class for Flask-Login
class User(UserMixin):
    def __init__(self, id, username, password):
        self.id = id
        self.username = username
        self.password = password

    @staticmethod
    def get(user_id):
        conn = get_db_connection()
        cursor = conn.cursor(dictionary=True)
        cursor.execute("SELECT id, username, password FROM users WHERE id = %s", (user_id,))
        user_data = cursor.fetchone()
        conn.close()
        if user_data:
            return User(user_data['id'], user_data['username'], user_data['password'])
        return None

    @staticmethod
    def get_by_username(username):
        conn = get_db_connection()
        cursor = conn.cursor(dictionary=True)
        cursor.execute("SELECT id, username, password FROM users WHERE username = %s", (username,))
        user_data = cursor.fetchone()
        conn.close()
        if user_data:
            return User(user_data['id'], user_data['username'], user_data['password'])
        return None

@login_manager.user_loader
def load_user(user_id):
    return User.get(user_id)

# Function to generate a short URL
def generate_short_url(long_url):
    hash_object = hashlib.sha256(long_url.encode())
    short_hash = base64.urlsafe_b64encode(hash_object.digest())[:6].decode()
    return short_hash

# New routes for the new design
@app.route('/')
def new_home():
    return render_template('index_new.html')

@app.route('/shorten', methods=['POST'])
@login_required
def shorten_url_new():
    long_url = request.form.get('long_url')
    if not long_url:
        return redirect(url_for('new_home'))

    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)

    # Check if the long URL already exists for this user
    cursor.execute("SELECT short_url FROM url_mapping WHERE long_url = %s AND user_id = %s", (long_url, current_user.id))
    existing_entry = cursor.fetchone()

    if existing_entry:
        conn.close()
        short_url = existing_entry['short_url']
        flash(f"URL already shortened: <a href=\"{request.host_url}{short_url}\" target=\"_blank\">{request.host_url}{short_url}</a>", "error")
        return redirect(url_for('new_home'))

    # Generate new short URL
    short_url = generate_short_url(long_url)
    cursor.execute("INSERT INTO url_mapping (long_url, short_url, user_id) VALUES (%s, %s, %s)", (long_url, short_url, current_user.id))
    conn.commit()
    conn.close()
    flash(f"Shortened URL: <a href=\"{request.host_url}{short_url}\" target=\"_blank\">{request.host_url}{short_url}</a>", "success")
    return redirect(url_for('my_urls_new'))

@app.route('/login', methods=['GET', 'POST'])
def login_new():
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')

        conn = get_db_connection()
        cursor = conn.cursor(dictionary=True)
        cursor.execute("SELECT id, username, password FROM users WHERE username = %s", (username,))
        user_data = cursor.fetchone()
        conn.close()

        if user_data and check_password_hash(user_data['password'], password):
            user = User(user_data['id'], user_data['username'], user_data['password'])
            login_user(user)
            return redirect(url_for('new_home'))
        else:
            flash("Invalid username or password", "error")
            return redirect(url_for('login_new'))
    return render_template('login_new.html')

@app.route('/register', methods=['GET', 'POST'])
def register_new():
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')

        if not username or not password:
            flash("Username and password are required", "error")
            return redirect(url_for('register_new'))

        conn = get_db_connection()
        cursor = conn.cursor()
        
        # Check if username already exists
        cursor.execute("SELECT id FROM users WHERE username = %s", (username,))
        if cursor.fetchone():
            conn.close()
            flash("Username already exists", "error")
            return redirect(url_for('register_new'))

        hashed_password = generate_password_hash(password, method='pbkdf2:sha256')
        cursor.execute("INSERT INTO users (username, password) VALUES (%s, %s)", (username, hashed_password))
        conn.commit()
        conn.close()
        flash("Registration successful. Please login.", "success")
        return redirect(url_for('login_new'))
    return render_template('register_new.html')

@app.route('/my_urls')
@login_required
def my_urls_new():
    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)
    cursor.execute("SELECT long_url, short_url, clicks FROM url_mapping WHERE user_id = %s", (current_user.id,))
    user_urls = cursor.fetchall()
    conn.close()
    return render_template('my_urls_new.html', user_urls=user_urls)

@app.route('/logout_new')
@login_required
def logout_new():
    logout_user()
    return redirect(url_for('new_home'))

# Redirect shortened URLs
@app.route('/<short_url>', methods=['GET'])
def redirect_url(short_url):
    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)

    cursor.execute("SELECT long_url FROM url_mapping WHERE short_url = %s", (short_url,))
    entry = cursor.fetchone()

    if entry:
        cursor.execute("UPDATE url_mapping SET clicks = clicks + 1 WHERE short_url = %s", (short_url,))
        conn.commit()
        conn.close()
        return redirect(entry['long_url'])

    conn.close()
    return redirect(url_for('new_home'))

if __name__ == '__main__':
    app.run(host="0.0.0.0", port=5001, debug=True)
