import os
import uuid

import pandas as pd
from flask import Flask, request, render_template,Response,send_from_directory,jsonify

app = Flask(__name__,template_folder='templates')

@app.route('/', methods=['GET','POST'])
def index1():
    if request.method == 'GET':
        return render_template('index1.html')

    elif request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')

        if username == 'hello' and password == 'password':
            return 'Success'
        else:
            return 'Failure'

@app.route('/file_upload',methods=['POST'])
def upload():
    file = request.files["file"]
    if file.content_type == 'text/plain':
        return file.read().decode()
    elif file.content_type == 'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet' or file.content_type == 'application/vnd.ms-excel':
        df = pd.read_excel(file)
        return df.to_html()
    else:
        return "Invalid file format"

@app.route('/convert_to_csv',methods=['POST'])
def to_csv():
    file = request.files["file"]
    if file.content_type == 'text/plain':
        df = pd.read_csv('file')
        response = Response(
        df.to_csv(),mimetype='text/csv',headers={
                'Content-Disposition':'attachment;filename = result.csv'
            }
        )
        return response

    elif file.content_type == 'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet' or file.content_type == 'application/vnd.ms-excel':
        df = pd.read_excel(file)
        response = Response(
        df.to_csv(),mimetype='text/csv',headers={
                'Content-Disposition':'attachment;filename = result.csv'
            }
        )
        return response


@app.route('/convert_csv_two',methods=['POST'])
def convert_csv_two():
    file = request.files["file"]
    df = pd.read_excel(file)

    if not os.path.exists('downloads'):
        os.makedirs('downloads')

    filename = f'{uuid.uuid4()}.csv'
    df.to_csv(os.path.join('downloads',filename))

    return render_template('download.html',filename = filename)

@app.route('/downloads/<filename>')
def downloads(filename):
    return send_from_directory('downloads',filename,download_name = 'result.csv')

@app.route('/handle_post',methods=['POST'])
def handle_post():
    greeting = request.json['greeting']
    name = request.json['name']

    with open(file.txt) as f:
        f.write(f"{greeting},{name}")

    return jsonify({'Message': "successfully written!"})


if __name__ == "__main__":
    app.run(host='0.0.0.0',port=5555,debug = True)


