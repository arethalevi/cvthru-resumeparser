import os
from flask import Flask, render_template, request, redirect, url_for, abort
from werkzeug.utils import secure_filename
from functions import resume_parse
import json
from flask_dropzone import Dropzone



app = Flask(__name__)
app.config['UPLOAD_EXTENSIONS'] = ['.pdf','.docx']
app.config['UPLOAD_PATH'] = 'static/uploadedfile'

dropzone = Dropzone(app)

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/upload')
def upload():
    return render_template('upload.html')

@app.route('/submit', methods=['GET','POST'])
def submit():
    if request.method == 'POST':
        uploaded_file = request.files['file']
        filename = secure_filename(uploaded_file.filename)
        if filename != '':
            file_ext = os.path.splitext(filename)[1]
            if file_ext not in app.config['UPLOAD_EXTENSIONS']:
                return render_template('unsuf.html')
            img_path = os.path.join(app.config['UPLOAD_PATH'], filename)
            print(img_path)
            uploaded_file.save(img_path)
            jj = resume_parse(img_path)
            jj['path']=filename
            jes = json.dumps(jj)
            loaded = json.loads(jes)
        return render_template('output.html',linked=loaded)

if __name__ =="__main__":
    app.run(debug=True)
