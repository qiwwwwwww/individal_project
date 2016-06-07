from app import app
from flask import Flask, request, flash, redirect, url_for, render_template,make_response
import gridfs
from pymongo import MongoClient 
from werkzeug.utils import secure_filename
from gridfs.errors import NoFile
from bson.objectid import ObjectId

ALLOWED_EXTENSIONS = set(['apk'])
fs = gridfs.GridFS(MongoClient().pancake)


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
    		return redirect(url_for('upload_file', oid=str(oid)))

    return '''
    <!doctype html>
    <html>
    <head>
    <title>Upload new File</title>
    </head>
    <body>
    <h1>Upload new File</h1>
    <form action="" method="post" enctype="multipart/form-data">
      <p><input type="file" name="file">
         <input type="submit" value="Upload">
    </form>
    <a href="%s">All files</a>
    </body>
    </html>
    ''' % url_for('list_gridfs_files')



@app.route('/files')
def list_gridfs_files():
    files = [fs.get_last_version(file) for file in fs.list()]
    file_list = "\n".join(['<li><a href="%s">%s</a></li>' % \
                            (url_for('serve_gridfs_file', oid=str(file._id)), file.name) \
                            for file in files])
    return '''
    <!DOCTYPE html>
    <html>
    <head>
    <title>Files</title>
    </head>
    <body>
    <h1>Files</h1>
    <ul>
    %s
    </ul>
    <a href="%s">Upload new file</a>
    </body>
    </html>
    ''' % (file_list, url_for('upload_file'))

@app.route('/files/<oid>')
def serve_gridfs_file(oid):
    try:
        file = fs.get(ObjectId(oid))
        response = make_response(file.read())
        response.mimetype = file.content_type
        return response
    except NoFile:
        abort(404)

