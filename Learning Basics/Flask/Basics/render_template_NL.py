from flask import Flask,request,make_response,render_template
app = Flask(__name__,template_folder='templates')

@app.route('/')
def index():
    my = [1,2,3,4,5,6]
    return render_template('index.html',my = my)

if __name__ == "__main__":
    app.run(host='0.0.0.0',port=5555,debug = True)
