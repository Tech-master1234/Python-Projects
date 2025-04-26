from flask import Flask,render_template,session,make_response,request,flash
app = Flask(__name__,template_folder='templates')

app.secret_key = '123456'

@app.route('/')
def index():
    return render_template('sess.html',message = 'session not set')

@app.route('/set_data')
def set_data():
        session['fname'] = 'Manoj'
        session['lname'] = 'bharathi'
        return render_template('sess.html',message = 'session is set')

@app.route('/get_data')
def get_data():
    if 'fname' in session.keys() and 'lname' in session.keys():
        fname = session['fname']
        lname = session['lname']
        return render_template('sess.html', message=f'Name:{fname} {lname}')
    else:
            return render_template('sess.html',message = 'You deleted the session cookie')

@app.route('/clear_data')
def clear_data():
    session.clear()
    return render_template('sess.html', message= 'Session cleared')

@app.route('/set_cookie')
def set_cookie():
    response = make_response(render_template('sess.html',message = 'Cookie set'))
    response.set_cookie('cookie_name','cookie_value')
    return response

@app.route('/get_cookie')
def get_cookie():
    cookie_value = request.cookies['cookie_value']
    return render_template('sess.html', message= cookie_value)

@app.route('/remove_cookie')
def remove_cookie():
    response = make_response(render_template('sess.html',message = 'Cookie removed'))
    response.set_cookie('cookie_name',expires=20)
    return response

@app.route('/login',methods = ['GET','POST'])
def login():
    if request.method == 'GET':
        return render_template('login page.html')
    elif request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')
        if username == 'manoj' and password == 'mano':
            flash('Login success!')
            return render_template('sess.html',message = '')
        else:
            #flash('Login failed!')
            return render_template('sess.html',message = '')


if __name__ == "__main__":
    app.run(host='0.0.0.0',port=5555,debug = True)
