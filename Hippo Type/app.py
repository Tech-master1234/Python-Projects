from flask import Flask, render_template, send_from_directory, session, request, redirect, url_for, flash, jsonify
import os
import json
from datetime import datetime
from werkzeug.security import generate_password_hash, check_password_hash
from typing import Dict, List

app = Flask(__name__)
app.secret_key = os.urandom(24)  # Required for session

SCORES_FILE = 'scores.json'
USERS_FILE = 'users.json'
LEVELS_FILE = 'typing_levels.json'

def load_levels() -> Dict:
    try:
        with open(LEVELS_FILE, 'r') as f:
            return json.load(f)
    except FileNotFoundError:
        return {}

def load_users() -> Dict:
    try:
        with open(USERS_FILE, 'r') as f:
            return json.load(f)
    except FileNotFoundError:
        return {}

def save_users(users: Dict) -> None:
    with open(USERS_FILE, 'w') as f:
        json.dump(users, f, indent=4)

def load_scores():
    if not os.path.exists(SCORES_FILE):
        return []
    with open(SCORES_FILE, 'r') as f:
        return json.load(f)

def save_scores(scores):
    with open(SCORES_FILE, 'w') as f:
        json.dump(scores, f)

def save_score(username, wpm, accuracy):
    score = wpm * (accuracy / 100)  # Calculate score based on WPM and accuracy
    scores = load_scores()
    scores.append({
        'username': username,
        'wpm': wpm,
        'accuracy': accuracy,
        'score': score,
        'date': datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    })
    # Sort by score in descending order
    scores.sort(key=lambda x: x['score'], reverse=True)
    # Keep only top 10 scores
    scores = scores[:10]
    save_scores(scores)

def get_leaderboard():
    scores = load_scores()
    return scores

@app.route('/')
def index():
    if 'username' not in session:
        return redirect(url_for('login'))
    return redirect(url_for('levels'))

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')
        users = load_users()
        
        if username in users and check_password_hash(users[username]['password'], password):
            session['username'] = username
            return redirect(url_for('index'))
        else:
            flash('Invalid username or password')
            return redirect(url_for('login'))
    return render_template('login.html')

@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')
        confirm_password = request.form.get('confirm_password')
        
        if not username or not password:
            flash('Username and password are required')
            return redirect(url_for('register'))
        
        if password != confirm_password:
            flash('Passwords do not match')
            return redirect(url_for('register'))
        
        users = load_users()
        if username in users:
            flash('Username already exists')
            return redirect(url_for('register'))
        
        users[username] = {
            'password': generate_password_hash(password)
        }
        save_users(users)
        flash('Registration successful! Please login.')
        return redirect(url_for('login'))
    
    return render_template('register.html')

@app.route('/logout')
def logout():
    session.pop('username', None)
    return redirect(url_for('login'))

@app.route('/save_score', methods=['POST'])
def save_score_route():
    if 'username' not in session:
        return redirect(url_for('login'))
    
    data = request.get_json()
    wpm = data.get('wpm')
    accuracy = data.get('accuracy')
    
    if wpm and accuracy:
        save_score(session['username'], wpm, accuracy)
        return {'status': 'success'}
    return {'status': 'error'}

@app.route('/levels')
def levels():
    if 'username' not in session:
        return redirect(url_for('login'))
    
    users = load_users()
    user_progress = users.get(session['username'], {}).get('progress', 1)
    
    return render_template('levels.html', user_progress=user_progress)

@app.route('/play/<int:level>')
def play_level(level: int):
    if 'username' not in session:
        return redirect(url_for('login'))
    
    users = load_users()
    user_progress = users.get(session['username'], {}).get('progress', 1)
    
    if level > user_progress:
        flash('You need to complete previous levels first!', 'error')
        return redirect(url_for('levels'))
    
    levels_data = load_levels()
    level_key = f'level{level}'
    
    
    
    if level_key not in levels_data:
        flash('Level not found!', 'error')
        return redirect(url_for('levels'))
    
    words = levels_data[level_key]['words']
    return render_template('index.html', words=words, current_level=level)

@app.route('/complete_level', methods=['POST'])
def complete_level():
    if 'username' not in session:
        return jsonify({'error': 'Not logged in'}), 401
    
    data = request.get_json()
    level = data.get('level')
    score = data.get('score')
    accuracy = data.get('accuracy')
    wpm = data.get('wpm')
    
    if not level or not score or not accuracy or not wpm:
        return jsonify({'error': 'Missing required data'}), 400
    
    levels_data = load_levels()
    level_key = f'level{level}'
    level_wpm = levels_data[level_key]['wpm']
    level_accuracy = levels_data[level_key]['accuracy']
    
    # Check if requirements are met
    if accuracy < level_accuracy or wpm < level_wpm:
        return jsonify({
            'error': 'Level requirements not met',
            'message': f'You need at least {level_accuracy}% accuracy and {level_wpm} WPM to complete this level'
        }), 400
    
    users = load_users()
    username = session['username']
    
    if username not in users:
        return jsonify({'error': 'User not found'}), 404
    
    user_data = users[username]
    current_progress = user_data.get('progress', 1)
    
    # Update progress if this is the next level
    if level == current_progress:
        user_data['progress'] = current_progress + 1
    
    # Update high score for this level if it's higher
    level_scores = user_data.get('level_scores', {})
    current_high_score = level_scores.get(str(level), 0)
    if score > current_high_score:
        level_scores[str(level)] = score
        user_data['level_scores'] = level_scores
    
    save_users(users)
    return jsonify({'success': True})

@app.route('/leaderboard')
def leaderboard():
    if 'username' not in session:
        return redirect(url_for('login'))
    
    scores = get_leaderboard()
    return render_template('leaderboard.html', scores=scores)

@app.route('/static/<path:filename>')
def serve_static(filename):
    return send_from_directory('static', filename)

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=True)