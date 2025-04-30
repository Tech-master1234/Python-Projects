from flask import Flask, render_template, request, jsonify
from flask_cors import CORS
import main  # our existing password manager
import os
from functools import wraps
import jwt
from datetime import datetime, timedelta
import json

app = Flask(__name__)
CORS(app)
app.config['SECRET_KEY'] = os.getenv('SECRET_KEY','default_dev_key')

if not app.config['SECRET_KEY']:
    raise RuntimeError("SECRET_KEY is not set! Please set it as an environment variable.")

USERS_FILE = 'users.json'

def load_users():
    if os.path.exists(USERS_FILE):
        with open(USERS_FILE, 'r') as f:
            return json.load(f)
    return {}

def save_users(users):
    with open(USERS_FILE, 'w') as f:
        json.dump(users, f, indent=4)

def token_required(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        token = request.args.get('token')
        if not token:
            return jsonify({'message': 'Token is missing'}), 401
        try:
            jwt.decode(token, app.config['SECRET_KEY'], algorithms=["HS256"])
        except:
            return jsonify({'message': 'Invalid token'}), 401
        return f(*args, **kwargs)
    return decorated

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/register', methods=['POST'])
def register():
    username = request.json.get('username')
    password = request.json.get('password')
    confirm_password = request.json.get('confirm_password')
    
    if not username or not password or not confirm_password:
        return jsonify({'error': 'All fields are required'}), 400
        
    if password != confirm_password:
        return jsonify({'error': 'Passwords do not match'}), 400
    
    users = load_users()
    
    if username in users:
        return jsonify({'error': 'Username already exists'}), 400
    
    # Hash the password before storing
    salt = main.get_or_create_salt()
    key = main.derive_key(password, salt)
    
    # Store user with hashed password
    users[username] = {
        'password_hash': key.hex(),
        'salt': salt.hex(),
        'created_at': datetime.utcnow().isoformat()
    }
    
    save_users(users)
    return jsonify({'message': 'Registration successful'})

@app.route('/login', methods=['POST'])
def login():
    username = request.json.get('username')
    master_password = request.json.get('password')
    
    if not username or not master_password:
        return jsonify({'error': 'Username and password are required'}), 400
    
    users = load_users()
    if username not in users:
        return jsonify({'error': 'Invalid username'}), 401
    
    try:
        # Verify password using stored hash
        user = users[username]
        salt = bytes.fromhex(user['salt'])
        stored_key = bytes.fromhex(user['password_hash'])
        key = main.derive_key(master_password, salt)
        
        if key != stored_key:
            return jsonify({'error': 'Invalid password'}), 401
        
        # Generate token
        token = jwt.encode({
            'username': username,
            'exp': datetime.utcnow() + timedelta(hours=1)
        }, app.config['SECRET_KEY'])
        
        return jsonify({'token': token})
    except Exception as e:
        return jsonify({'error': 'Invalid credentials'}), 401

@app.route('/passwords', methods=['GET'])
@token_required
def get_passwords():
    search_term = request.args.get('search', '')
    master_password = request.args.get('master_password')
    salt = main.get_or_create_salt()
    key = main.derive_key(master_password, salt)
    results = main.search_passwords(key, search_term)
    return jsonify(results)

@app.route('/passwords', methods=['POST'])
@token_required
def add_password():
    data = request.json
    master_password = data.get('master_password')
    entry = {
        'website': data.get('website'),
        'username': data.get('username'),
        'email': data.get('email'),
        'password': data.get('password'),
        'recovery': data.get('recovery')
    }
    salt = main.get_or_create_salt()
    key = main.derive_key(master_password, salt)
    encrypted_entry = main.encrypt_entry(entry, key)
    main.save_encrypted_entry(encrypted_entry)
    return jsonify({'message': 'Password saved successfully'})

@app.route('/passwords/<int:index>', methods=['PUT'])
@token_required
def update_password(index):
    data = request.json
    master_password = data.get('master_password')
    entry = {
        'website': data.get('website'),
        'username': data.get('username'),
        'email': data.get('email'),
        'password': data.get('password'),
        'recovery': data.get('recovery')
    }
    try:
        salt = main.get_or_create_salt()
        key = main.derive_key(master_password, salt)
        
        # Load existing passwords
        with open('passwords.json', 'r') as f:
            passwords = json.load(f)
        
        if 0 <= index < len(passwords):
            # Encrypt and update the entry
            encrypted_entry = main.encrypt_entry(entry, key)
            passwords[index] = encrypted_entry
            
            # Save back to file
            with open('passwords.json', 'w') as f:
                json.dump(passwords, f, indent=4)
            
            return jsonify({'message': 'Password updated successfully'})
        else:
            return jsonify({'error': 'Invalid password index'}), 404
            
    except Exception as e:
        return jsonify({'error': str(e)}), 500

if __name__ == '__main__':
    app.run(debug=True)