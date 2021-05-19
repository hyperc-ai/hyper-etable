# Serve the excel backend service over http

import os
from flask import Flask, flash, request, redirect, url_for, send_file
from werkzeug.utils import secure_filename

import hyper_etable.etable

UPLOAD_FOLDER = '/tmp'
ALLOWED_EXTENSIONS = {'xlsx', 'xlsm'}

app = Flask(__name__)
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

SOLVED_FILES = {}

def allowed_file(filename):
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

@app.route('/xlsolve', methods=['GET', 'POST'])
def upload_file():
    if request.method == 'POST':
        # check if the post request has the file part
        if 'file' not in request.files:
            flash('No file part')
            print("No file part")
            return redirect(request.url)
        file = request.files['file']
        print("file part found")
        # If the user does not select a file, the browser submits an
        # empty file without a filename.
        if file.filename == '':
            flash('No selected file')
            print('No selected file')
            return redirect(request.url)
        print('selected file found')
        if file and allowed_file(file.filename):
            print('file allowed')
            filename = secure_filename(file.filename)
            full_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
            file.save(full_path)
            et = hyper_etable.etable.ETable(full_path, filename.replace(".", "_").replace("/", "_"))
            SOLVED_FILES[filename] = et.calculate()

            # return redirect(url_for('download_file', name=filename))
        else:
            print('file not allowed')
    return '''
    <!doctype html>
    <title>Upload new File</title>
    <h1>Upload new File</h1>
    <form method=post enctype=multipart/form-data>
      <input type=file name=file>
      <input type=submit value=Upload>
    </form>
    '''


@app.route('/check', methods=['GET'])
def check():
    return "OK"


@app.route('/xlsolution/<filename>', methods=['GET'])
def xlsolution(filename):
    # return send_from_directory(directory='pdf', filename=filename)
    return send_file(SOLVED_FILES[filename], as_attachment=True)


app.run(port=8493)