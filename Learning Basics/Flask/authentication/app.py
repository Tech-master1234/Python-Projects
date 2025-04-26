
from flask import Flask,url_for,redirect
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from flask_login import LoginManager
from flask_bcrypt import Bcrypt

db = SQLAlchemy()

def create_app():
    app = Flask(__name__ ,template_folder='templates')
    #app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///./test.db'
    app.config['SQLALCHEMY_DATABASE_URI'] = 'postgresql://postgres:postgres@localhost:5432/authenticationdb'

    app.secret_key = 'SOME KEY'

    db.init_app(app)

    login_manager = LoginManager()
    login_manager.init_app(app)

    @login_manager.unauthorized_handler
    def unauthorized_callback():
        return 'Custom Behaviour'



    from model import User
    @login_manager.user_loader
    def load_user(uid):
        return User.query.get(uid)

    bcrypt = Bcrypt(app)

    from routes import register_routes
    register_routes(app,db,bcrypt)

    #migrate = Migrate(app,db)

    return app