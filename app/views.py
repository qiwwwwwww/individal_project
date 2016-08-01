from app import app, oauth2, session
from flask import Flask, request, flash, redirect, url_for, render_template,make_response
from flask import json as fJson
import gridfs
from pymongo import MongoClient
from werkzeug.utils import secure_filename
from gridfs.errors import NoFile
from bson.objectid import ObjectId
from .forms import DetailForm
import json


ALLOWED_EXTENSIONS = set(['apk'])
ALLOWED_EXTENSIONS_02 = set(['png','jpg'])
ALLOWED_EXTENSIONS_03 = set(['json'])

db=MongoClient().pancake
fs = gridfs.GridFS(db)
appstore=db.appstore
jsonstore = db.jsonstore

def allowed_file(filename):
    return '.' in filename and \
        filename.rsplit('.', 1)[1] in ALLOWED_EXTENSIONS

def allowed_file_02(filename):
    return '.' in filename and \
        filename.rsplit('.', 1)[1] in ALLOWED_EXTENSIONS_02  

def allowed_file_03(filename):
    return '.' in filename and \
        filename.rsplit('.', 1)[1] in ALLOWED_EXTENSIONS_03  

@app.route('/upload', methods=['GET', 'POST'])
@oauth2.required
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
            return redirect(url_for('next', oid=str(oid)))
        
    return render_template('upload_file.html')

@app.route('/next/<string:oid>', methods=['GET','POST'])
def next(oid):
    form = DetailForm()
    if form.validate_on_submit():
        if 'profile' in session:
            appstore.insert_one({
            'title': form.title.data,
            'description': form.description.data,
            'apkid':ObjectId(oid),
            'category':form.category.data,
            'createdBy': session['profile']['displayName'],
            'createdById': session['profile']['id']

            })
            return redirect(url_for('img_upload', oid=oid))
    return render_template('next.html', form=form)
 

@app.route('/img/<string:oid>', methods=['GET', 'POST'])
@oauth2.required
def img_upload(oid):
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
        if file and allowed_file_02(file.filename):
            filename = secure_filename(file.filename)
            oid_02 = fs.put(file, content_type=file.content_type, filename=filename)
            appstore.update_one(
                {"apkid": ObjectId(oid)},
                { "$set": {"img_id": ObjectId(oid_02)}}
                )
            return redirect(url_for('json_upload', oid=oid))
        
    return render_template('upload_file.html')
    #         return redirect(url_for('list_gridfs_files'))
        
    # return render_template('upload_file.html')

@app.route('/json/<string:oid>', methods=['GET', 'POST'])
@oauth2.required
def json_upload(oid):
    if request.method == 'POST':
        # check if the post request has the file part
        if 'file' not in request.files:
            flash('No file part')
            return redirect(request.url)
        file = request.files['file']

        if file.filename == '':
            flash('No selected file')
            return redirect(request.url)
        if file and allowed_file_03(file.filename):
            filename = secure_filename(file.filename)
            myfile=file.read()
            incident=json.loads(myfile)
            appstore.update_one(
                {"apkid": ObjectId(oid)},
                { "$set": incident}
                )
            return redirect(url_for('list_gridfs_files'))
        
    return render_template('upload_file.html')



@app.route('/files')
def list_gridfs_files():
    files = appstore.find()
    # files = [fs.get_last_version(file) for file in fs.list()]
    # oid=[str(file._id) for file in files] 
    return render_template('list_gridfs_files.html', files=files)   

@app.route('/files/<id>')
def detail(id):
    file=appstore.find_one({'_id': ObjectId(str(id))})
    return render_template('detail.html', file=file)


@app.route('/mine')
@oauth2.required
def list_mine():
    user_id=session['profile']['id']
    files = appstore.find({'createdById': user_id})
    return render_template('user.html', files=files)


@app.route('/files/<id>/remove')
def remove(id):
    appstore.remove({'_id': ObjectId(str(id))})
    return render_template('user.html')


@app.route('/files/<id>/edit', methods=['GET', 'POST'])
def edit(id):
    file=appstore.find_one({'_id': ObjectId(str(id))})
    form = DetailForm()

    if request.method == 'POST':
        file=appstore.update(
            {'_id': ObjectId(str(id))},
            {"$set":{
            'title': form.title.data,
            'description': form.description.data,
            'category':form.category.data,
            }
            }
            )
        return render_template('detail.html', file=file)
    return render_template("next.html", action="Edit", file=file, form=form)



@app.route('/show/<oid>')
def serve_gridfs_file(oid):
    try:
        file = fs.get(ObjectId(oid))
        response = make_response(file.read())
        response.mimetype = file.content_type
        return response
    except NoFile:
        abort(404)


    
@app.route('/logout')
def logout():
    # Delete the user's profile and the credentials stored by oauth2.
    del session['profile']
    session.modified = True
    oauth2.storage.delete()
    return redirect(request.referrer or '/')