import os
import time
from flask import Flask, request, render_template

import main_web
# import user

app = Flask(__name__, static_folder='.', static_url_path='')
# UPLOAD_FOLDER = user.name
UPLOAD_FOLDER = "upload"
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

@app.route('/', methods=['POST'])
def upload_file():
    #f = request.files['chord']
    f = open('upload/tmp.txt', 'w')
    Mm=request.form.get('Mm')
    sign=request.form.get('tonic')
    if Mm=='M':
        sign=sign.split('/')[0]
    elif Mm=='m':
        sign=sign.split('/')[1]

    f.write("key:"+sign+"\n")
    bpm=request.form.get('bpm')
    f.write("bpm:"+bpm+"\n")
    f.write(request.form.get('chord'))
    f.close()
    #f.save(os.path.join(app.config['UPLOAD_FOLDER'], 'tmp.txt'))
    main_web.txt_to_mid(os.path.join(app.config['UPLOAD_FOLDER'], 'tmp.txt'),'output/tmp')
    key = "output/tmp-1.png?"+str(int(time.time()))
    return render_template('finished.html',key=key)

@app.route('/', methods=['GET'])
def upload_file_view():
    return render_template('upload.html')


app.run(port=8000, debug=True)