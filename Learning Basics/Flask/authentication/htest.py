from flask import Flask,render_template
app = Flask(__name__,template_folder='templates')


@app.route('/')
def sign():
    return render_template('signup.html')

@app.route('/login')
def log():
    return render_template('login.html')

if __name__ == '__main__':
    app.run(host='0.0.0.0',debug=True)