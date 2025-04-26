from flask import render_template,request,redirect,url_for
from model import User
from flask_login import login_user,logout_user,current_user,login_required




def register_routes(app,db,bcrypt):
    @app.route('/')
    def index():
        return render_template('index.html')

    @app.route('/signup',methods=['POST','GET'])
    def signup():
        if request.method == 'GET':
            return render_template('signup.html')

        elif request.method == 'POST':
            username = request.form.get('username')
            password = request.form.get('password')

            user = User.query.filter(User.username == username).first()
            if user:
                return 'User already exists'

            else:

                hashed_password = bcrypt.generate_password_hash(password).decode('utf-8')

                user = User(username=username,password=hashed_password)

                db.session.add(user)
                db.session.commit()
                login_user(user)
                return redirect(url_for('index'))

    @app.route('/login',methods=['POST','GET'])
    def login():
        if request.method == 'GET':
            return render_template('login.html')
        elif request.method == 'POST':
            username = request.form.get('username')
            password = request.form.get('password')


            user = User.query.filter(User.username == username).first()
            if bcrypt.check_password_hash(user.password,password):
                login_user(user)
                return redirect(url_for('index'))
            else:
                return "failure"



    @app.route('/secret')
    @login_required
    def secret():
        return 'i hate my job'





    @app.route('/logout')
    def logout():
        logout_user()
        return render_template('index.html')



















    '''
    @app.route('/',methods= ['POST','GET'])
    def index():
        if current_user.is_authenticated:
            return str(current_user.username)
        else:
            return 'No user logged in'

    @app.route('/login/<uid>')
    def login(uid):
        user = User.query.get(uid)
        login_user(user)
        return 'login success'

    @app.route('/logout')
    def logout():
        logout_user()
        return 'logged out'
'''


