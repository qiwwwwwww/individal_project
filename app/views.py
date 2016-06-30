from app import app
from flask import Flask, request, flash, redirect, url_for, render_template,make_response
import gridfs
from pymongo import MongoClient
from werkzeug.utils import secure_filename
from gridfs.errors import NoFile
from bson.objectid import ObjectId
from .forms import DetailForm


ALLOWED_EXTENSIONS = set(['apk'])
db=MongoClient().pancake
fs = gridfs.GridFS(db)
good=db.good

def allowed_file(filename):
    return '.' in filename and \
    	filename.rsplit('.', 1)[1] in ALLOWED_EXTENSIONS
    

@app.route('/', methods=['GET', 'POST'])
def upload_file():
    if request.method == 'POST':
        # check if the post request has the file part
        if 'file' not in request.files:
            flash('No file part')
            return redirect(request.url)
        file = request.files['file']
        # if user does not select file, browser also
        # submit a empty part without filename
        if file.filename == '':
            flash('No selected file')
            return redirect(request.url)
        if file and allowed_file(file.filename):
            filename = secure_filename(file.filename)
            oid = fs.put(file, content_type=file.content_type, filename=filename)
            # good.insert_one({'name': 'cupcake'})
            return redirect(url_for('next', oid=str(oid)))
        
    return render_template('upload_file.html')


@app.route('/files')
def list_gridfs_files():
    files = [fs.get_last_version(file) for file in fs.list()]
    oid=[str(file._id) for file in files] 
    return render_template('list_gridfs_files.html',oid =oid, files=files)   


@app.route('/remove/<filename>')
def remove_gridfs_files(filename):
    db.fs.files.remove({"filename": filename})
    return render_template('remove.html', filename=filename, file=file)



@app.route('/files/<oid>')
def serve_gridfs_file(oid):
    try:
        file = fs.get(ObjectId(oid))
        response = make_response(file.read())
        response.mimetype = file.content_type
        return response
    except NoFile:
        abort(404)

@app.route('/next/<string:oid>', methods=['GET','POST'])
def next(oid):
    form = DetailForm()
    if form.validate_on_submit():
        good.insert_one({
        'title': form.title.data,
        'description': form.description.data,
        'apkid':oid
        })
        return redirect(url_for('list_gridfs_files'))
    return render_template('next.html', form=form)
    
