from flask import Flask,render_template
app = Flask(__name__,template_folder='login_page_1')
@app.route('/')
@app.route('/home')
def hi():
    return render_template("index.html")


__name__ == "__main__"
app.run(debug= True)