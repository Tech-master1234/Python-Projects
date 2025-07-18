import os
import os
import binascii
import time
from flask import Flask, render_template, request, redirect, url_for, flash
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager, UserMixin, login_user, logout_user, login_required, current_user
from werkzeug.security import generate_password_hash, check_password_hash
import threading
import subprocess
import datetime
from appdirs import user_data_dir


main = Flask(__name__, template_folder='templates')
API_SECRET_KEY_FILE = "API_SECRET_KEY"

API_SECRET_KEY = os.environ.get("API_SECRET_KEY","API_SECRET_KEY")

if not API_SECRET_KEY:
        secret_key = binascii.hexlify(os.urandom(24)).decode()
        with open(API_SECRET_KEY_FILE, "w") as f:
            f.write(secret_key)
        print(f"Secret key generated and saved to '{API_SECRET_KEY_FILE}'.")
        API_SECRET_KEY = secret_key

main.config['SECRET_KEY'] = API_SECRET_KEY

APP_NAME = "BeSync"
APP_AUTHOR = "Tech-master1234"
data_dir = user_data_dir(APP_NAME, APP_AUTHOR)
if not os.path.exists(data_dir):
    os.makedirs(data_dir)
db_path = os.path.join(data_dir, 'users.db')
main.config['SQLALCHEMY_DATABASE_URI'] = f'sqlite:///{db_path}'
db = SQLAlchemy(main)
login_manager = LoginManager()
login_manager.init_app(main)
login_manager.login_view = 'login'

# Settings model
class Settings(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    multi_device_access = db.Column(db.Boolean, default=False)
    dark_mode = db.Column(db.Boolean, default=False)

@main.route('/settings', methods=['GET', 'POST'])
@login_required
def settings():
    if not current_user.is_admin:
        flash("You do not have permission to access this page.")
        return redirect(url_for('index'))

    settings = Settings.query.first()
    if not settings:
        settings = Settings(multi_device_access=False, dark_mode=False)
        db.session.add(settings)
        db.session.commit()

    if request.method == 'POST':
        settings.multi_device_access = 'multi_device_access' in request.form
        db.session.commit()
        flash('Settings updated successfully!')
        return redirect(url_for('settings'))

    return render_template('settings.html', settings=settings)

# User model
class User(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    password_hash = db.Column(db.String(120), nullable=False)
    role = db.Column(db.String(20), default='user', nullable=False) # 'admin' or 'user'

    def set_password(self, password):
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.password_hash, password)

    @property
    def is_admin(self):
        return self.role == 'admin'

# Task model
class Task(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    method = db.Column(db.String(10), nullable=False) # 'Backup', 'Sync', or 'Bi-Sync'
    source = db.Column(db.String(255), nullable=False)
    destination = db.Column(db.String(255), nullable=False)
    schedule_type = db.Column(db.String(10), default='interval') # 'interval' or 'specific_time'
    interval_seconds = db.Column(db.Integer, default=0)
    run_at = db.Column(db.Time, nullable=True) # For specific time scheduling
    status = db.Column(db.String(20), default='Stopped') # 'Running', 'Stopped', 'Error'
    last_run = db.Column(db.DateTime, nullable=True)

    user = db.relationship('User', backref=db.backref('tasks', lazy=True))

@login_manager.user_loader
def load_user(user_id):
    return db.session.get(User, int(user_id))



@main.route('/', methods=['GET', 'POST'])
@login_required
def index():
    if request.method == 'POST':
        method = request.form.get('option')
        source = request.form.get('input-path')
        destination = request.form.get('output-path')
        if not destination:
            desktop_path = os.path.join(os.path.join(os.environ['USERPROFILE']), 'Desktop')
            destination = os.path.join(desktop_path, 'besync', method)
            if not os.path.exists(destination):
                os.makedirs(destination)
        
        schedule_type = request.form.get('schedule_type')
        run_at_time_str = request.form.get('run_at_time')
        
        interval_seconds = 0
        run_at = None

        if schedule_type == 'interval':
            days = int(request.form.get('days', 0))
            hours = int(request.form.get('hours', 0))
            minutes = int(request.form.get('minutes', 0))
            seconds = int(request.form.get('seconds', 0))
            interval_seconds = days * 86400 + hours * 3600 + minutes * 60 + seconds
        elif schedule_type == 'specific_time' and run_at_time_str:
            try:
                run_at = datetime.datetime.strptime(run_at_time_str, '%H:%M').time()
            except ValueError:
                flash('Invalid time format. Please use HH:MM.')
                return redirect(url_for('index'))

        new_task = Task(
            user_id=current_user.id,
            method=method,
            source=source,
            destination=destination,
            schedule_type=schedule_type,
            interval_seconds=interval_seconds,
            run_at=run_at
        )
        db.session.add(new_task)
        db.session.commit()
        flash('New task created successfully!')
        return redirect(url_for('index'))

    tasks = Task.query.filter_by(user_id=current_user.id).all()
    settings = Settings.query.first()
    return render_template('index.html', tasks=tasks, settings=settings)

@main.route('/all_tasks')
@login_required
def all_tasks():
    if not current_user.is_admin:
        flash("You do not have permission to access this page.")
        return redirect(url_for('index'))

    owner_filter = request.args.get('owner')
    method_filter = request.args.get('method')
    schedule_type_filter = request.args.get('schedule_type')
    status_filter = request.args.get('status')

    query = Task.query.join(User)

    if owner_filter:
        query = query.filter(User.username.ilike(f'%{owner_filter}%'))

    if method_filter:
        query = query.filter(Task.method == method_filter)

    if schedule_type_filter:
        query = query.filter(Task.schedule_type == schedule_type_filter)

    if status_filter:
        query = query.filter(Task.status == status_filter)

    tasks = query.all()
    settings = Settings.query.first()
    return render_template('all_tasks.html',
                           tasks=tasks,
                           settings=settings,
                           selected_owner=owner_filter,
                           selected_method=method_filter,
                           selected_schedule_type=schedule_type_filter,
                           selected_status=status_filter)

@main.route('/login', methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated:
        return redirect(url_for('index'))
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')
        user = User.query.filter_by(username=username).first()
        if user and user.check_password(password):
            login_user(user)
            return redirect(url_for('index'))
        else:
            flash('Invalid username or password')
    settings = Settings.query.first()
    return render_template('login.html', settings=settings)



@main.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect(url_for('login'))

@main.route('/admin/users')
@login_required
def admin_users():
    if not current_user.is_admin:
        flash("You do not have permission to access this page.")
        return redirect(url_for('index'))
    users = User.query.all()
    settings = Settings.query.first()
    return render_template('admin_users.html', users=users, settings=settings)

@main.route('/admin/delete_user/<int:user_id>', methods=['POST'])
@login_required
def delete_user_admin(user_id):
    if not current_user.is_admin:
        flash('You do not have permission to perform this action.')
        return redirect(url_for('index'))
    
    user = db.session.get(User, user_id)
    if not user:
        flash('User not found.')
        return redirect(url_for('admin_users'))
    
    if user.id == current_user.id:
        flash('You cannot delete your own account.')
        return redirect(url_for('admin_users'))

    # Prevent deletion of the primary admin (ID 1) by other admins
    if user.id == 1 and user.role == 'admin' and current_user.is_admin and current_user.id != user.id:
        flash('You cannot delete the primary admin account.')
        return redirect(url_for('admin_users'))

    # Delete associated tasks first
    Task.query.filter_by(user_id=user.id).delete()
    db.session.delete(user)
    db.session.commit()
    flash(f'User {user.username} and their tasks have been deleted.')
    return redirect(url_for('admin_users'))

@main.route('/admin/create_user', methods=['POST'])
@login_required
def create_user_admin():
    if not current_user.is_admin:
        flash('You do not have permission to create users.')
        return redirect(url_for('index'))
    
    username = request.form.get('username')
    password = request.form.get('password')
    role = request.form.get('role', 'user') # Default to 'user' if not provided

    if not username or not password:
        flash('Username and password are required.')
        return redirect(url_for('admin_users'))

    if User.query.filter_by(username=username).first():
        flash('Username already exists.')
        return redirect(url_for('admin_users'))

    new_user = User(username=username, role=role)
    new_user.set_password(password)
    db.session.add(new_user)
    db.session.commit()
    flash(f'User {username} ({role}) created successfully!')
    return redirect(url_for('admin_users'))

@main.route('/admin/change_user_credentials/<int:user_id>', methods=['GET', 'POST'])
@login_required
def change_user_credentials_admin(user_id):
    if not current_user.is_admin and current_user.id != user_id:
        flash('You do not have permission to change other users credentials.')
        return redirect(url_for('index'))

    user_to_edit = db.session.get(User, user_id)
    if not user_to_edit:
        flash('User not found.')
        return redirect(url_for('admin_users'))

    if request.method == 'POST':
        new_username = request.form.get('new_username')
        new_password = request.form.get('new_password')
        confirm_new_password = request.form.get('confirm_new_password')
        new_role = request.form.get('new_role')

        # Prevent other admins from changing the default admin's username or role
        if user_to_edit.id == 1 and user_to_edit.role == 'admin' and current_user.is_admin and current_user.id != user_to_edit.id:
            flash("You cannot change the primary admin's username or role.")
            return redirect(url_for('change_user_credentials_admin', user_id=user_id))

        if new_username and new_username != user_to_edit.username:
            if User.query.filter_by(username=new_username).first():
                flash('New username already taken.')
                return redirect(url_for('change_user_credentials_admin', user_id=user_id))
            user_to_edit.username = new_username

        if new_password:
            # Prevent other admins from changing the default admin's password
            if user_to_edit.username == 'admin' and user_to_edit.role == 'admin' and current_user.is_admin and current_user.id != user_to_edit.id:
                flash("You cannot change the default admin's password.")
                return redirect(url_for('change_user_credentials_admin', user_id=user_id))

            if new_password != confirm_new_password:
                flash('New password and confirm password do not match.')
                return redirect(url_for('change_user_credentials_admin', user_id=user_id))
            user_to_edit.set_password(new_password)
        
        if current_user.is_admin and new_role:
            user_to_edit.role = new_role

        db.session.commit()
        flash(f'Credentials for {user_to_edit.username} updated successfully!')
        return redirect(url_for('admin_users'))

    settings = Settings.query.first()
    return render_template('change_credentials.html', user=user_to_edit, settings=settings)

def execute_robocopy(source, destination, method):
    commands = []
    if method == 'Backup':
        commands.append(f'robocopy "{source}" "{destination}" /E /R:3 /W:5 /NP')
    elif method == 'Sync':
        commands.append(f'robocopy "{source}" "{destination}" /MIR /Z /R:3 /W:5 /NP')
    elif method == 'Bi-Sync':
        commands.append(f'robocopy "{source}" "{destination}" /E /R:3 /W:5 /NP /XO')
        commands.append(f'robocopy "{destination}" "{source}" /E /R:3 /W:5 /NP /XO')
    else:
        return False  # Invalid method

    for command in commands:
        try:
            result = subprocess.run(command, shell=True, capture_output=True, text=True)
            # Robocopy exit codes < 8 are considered success
            if result.returncode >= 8:
                raise subprocess.CalledProcessError(result.returncode, command, output=result.stdout, stderr=result.stderr)
            print(f"Robocopy Stdout: {result.stdout}")
            print(f"Robocopy Stderr: {result.stderr}")
        except subprocess.CalledProcessError as e:
            print(f"Robocopy Error: {e}")
            print(f"Robocopy Stdout: {e.stdout}")
            print(f"Robocopy Stderr: {e.stderr}")
            return False
    return True

# Dictionary to hold active task threads
active_task_threads = {}

def run_single_task(task_id):
    with main.app_context():
        task = Task.query.get(task_id)
        if not task:
            return

        while task.status == 'Running':
            if task.schedule_type == 'interval':
                print(f"Executing task {task.id}: {task.method} from {task.source} to {task.destination}")
                success = execute_robocopy(task.source, task.destination, task.method)
                if success:
                    task.last_run = datetime.datetime.now()
                    db.session.commit()
                    print(f"Task {task.id} completed successfully.")
                else:
                    task.status = 'Error'
                    db.session.commit()
                    print(f"Task {task.id} encountered an error.")
                    break # Stop on error

                if task.interval_seconds > 0:
                    time.sleep(task.interval_seconds)
                else:
                    # If interval is 0, run once and stop
                    task.status = 'Stopped'
                    db.session.commit()
                    print(f"Task {task.id} completed single run and stopped.")
                    break
            elif task.schedule_type == 'specific_time':
                now = datetime.datetime.now().time()
                # Calculate time until next run
                run_today = datetime.datetime.combine(datetime.date.today(), task.run_at)
                if now > task.run_at:
                    # If the time has passed today, schedule for tomorrow
                    next_run_time = run_today + datetime.timedelta(days=1)
                else:
                    next_run_time = run_today

                time_to_wait = (next_run_time - datetime.datetime.now()).total_seconds()
                if time_to_wait > 0:
                    print(f"Task {task.id} waiting for specific time: {task.run_at}. Sleeping for {time_to_wait} seconds.")
                    time.sleep(time_to_wait)
                
                # Re-fetch task to check for status changes (e.g., stopped by user)
                db.session.refresh(task)
                if task.status != 'Running':
                    break # Task was stopped while waiting

                print(f"Executing task {task.id}: {task.method} from {task.source} to {task.destination} at specific time.")
                success = execute_robocopy(task.source, task.destination, task.method)
                if success:
                    task.last_run = datetime.datetime.now()
                    db.session.commit()
                    print(f"Task {task.id} completed successfully at {task.run_at}.")
                else:
                    task.status = 'Error'
                    db.session.commit()
                    print(f"Task {task.id} encountered an error at {task.run_at}.")
                    break # Stop on error
            
            # Re-fetch task to check for status changes (e.g., stopped by user)
            db.session.refresh(task)

@main.route('/start_task/<int:task_id>')
@login_required
def start_task(task_id):
    task = db.session.get(Task, task_id)
    if not task:
        flash('Task not found.')
        return redirect(url_for('index'))
    if not current_user.is_admin and task.user_id != current_user.id:
        flash('You do not have permission to start this task.')
        return redirect(url_for('index'))

    if task.status != 'Running':
        task.status = 'Running'
        db.session.commit()
        # Start the task in a new thread
        thread = threading.Thread(target=run_single_task, args=(task.id,))
        thread.daemon = True # Allow the main program to exit even if threads are running
        thread.start()
        active_task_threads[task.id] = thread
        flash(f'Task {task.id} started.')
    else:
        flash(f'Task {task.id} is not running.')
    return redirect(url_for('index'))

@main.route('/stop_task/<int:task_id>')
@login_required
def stop_task(task_id):
    task = db.session.get(Task, task_id)
    if not task:
        flash('Task not found.')
        return redirect(url_for('index'))
    if not current_user.is_admin and task.user_id != current_user.id:
        flash('You do not have permission to stop this task.')
        return redirect(url_for('index'))

    if task.status == 'Running':
        task.status = 'Stopped'
        db.session.commit()
        # The run_single_task loop will pick up the status change and exit
        if task.id in active_task_threads:
            # Optionally, you could try to join the thread here if you need to wait for it to finish
            # For simplicity, we'll just let it naturally terminate
            del active_task_threads[task.id]
        flash(f'Task {task.id} stopped.')
    else:
        flash(f'Task {task.id} is not running.')
    return redirect(url_for('index'))

@main.route('/delete_task/<int:task_id>')
@login_required
def delete_task(task_id):
    task = db.session.get(Task, task_id)
    if not task:
        flash('Task not found.')
        return redirect(url_for('index'))
    if not current_user.is_admin and task.user_id != current_user.id:
        flash('You do not have permission to delete this task.')
        return redirect(url_for('index'))

    if task.status == 'Running':
        flash(f'Cannot delete task {task.id} while it is running. Please stop it first.')
    else:
        db.session.delete(task)
        db.session.commit()
        flash(f'Task {task.id} deleted.')
    return redirect(url_for('index'))



def restart_running_tasks():
    with main.app_context():
        running_tasks = Task.query.filter_by(status='Running').all()
        for task in running_tasks:
            print(f"Restarting task {task.id} that was running previously.")
            thread = threading.Thread(target=run_single_task, args=(task.id,))
            thread.daemon = True
            thread.start()
            active_task_threads[task.id] = thread

if __name__ == '__main__':
    with main.app_context():
        db.create_all() # Create database tables

        # Create default admin user if no users exist
        if User.query.count() == 0:
            admin_user = User(username='admin', role='admin')
            admin_user.set_password('admin')
            db.session.add(admin_user)
            db.session.commit()
            print("Default admin user created: username='admin', password='admin'")

        # Ensure a default settings entry exists
        settings = Settings.query.first()
        if not settings:
            settings = Settings(multi_device_access=False, dark_mode=False)
            db.session.add(settings)
            db.session.commit()

        restart_running_tasks()

        # Determine host based on multi_device_access setting
        app_host = '0.0.0.0' if settings.multi_device_access else '127.0.0.1'

    from waitress import serve
    serve(main, host=app_host, port=5010)

