from flask import Flask,request,make_response
app = Flask(__name__)

@app.route('/')
def h1():
    return 'hello'


@app.route('/hello')
def h2():
    response = make_response('Hello world\n')
    response.status_code = 203
    response.headers['content-type'] = 'plain/text'
    return response

@app.route('/greet/<name>')
def h3(name):
    return f"hello {name}"

@app.route('/url_request')
def url_request():
    if 'greeting' in request.args.keys() and 'naa' in request.args.keys():
        name = request.args.get('greeting')
        naa = request.args.get('naa')
        return f"{name} {naa}"
    else:
        return "parameters are missing"
if __name__ == "__main__":
    app.run(host='0.0.0.0',port=5555,debug = True)






    #GET POST METHOD
    '''
@app.route('/hello',methods=['GET','POST'])
def h2():
    if request.method == 'GET':
        return "You made a Get req"
    elif request.method == 'POST':
        return "You made a Post req"
    else:
        return "useless"
        '''