from flask import Flask,render_template,redirect,url_for
app = Flask(__name__,template_folder='templates')

@app.route('/')
def index():
    my = [1,2,3,4,5,6]
    return render_template('index.html',my = my)

@app.route('/other')
def other():
    h = "Hello world"
    return render_template('other.html',h = h)

@app.route('/home')
def home():
    return render_template('home.html')

@app.route('/about')
def about():
    return render_template('about.html')

@app.route('/redirect_endpoint')
def redirect_endpoint():
    return redirect(url_for('other'))

@app.template_filter
def reverse(s):
    return s[::-1]
if __name__ == "__main__":
    app.run(host='0.0.0.0',port=5555,debug = True)
