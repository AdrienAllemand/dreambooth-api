import os
import requests

from PIL import Image

from flaskr.auth import login_required
from flaskr.db import createTraining
from flask import (
    Blueprint, flash, redirect, render_template, request, current_app, g, send_from_directory, url_for,
)
from werkzeug.utils import secure_filename

url = "http://localhost:5001/train"

ALLOWED_EXTENSIONS = set(['png'])

bp = Blueprint('images', __name__, url_prefix='/images')

@bp.route('/upload', methods=['GET','POST'])
@login_required
def upload():
    if request.method == "POST":
        files = request.files.getlist("file")
        if files is None:
            flash("No files uploaded")
        elif g.user['id'] is None:
            flash("No user logged in")
        else:
            userPath = os.path.join(current_app.config['UPLOAD_FOLDER'], secure_filename(str(g.user['id'])))
            try:
                print("Creating upload folder: " + userPath)
                os.makedirs(userPath)
            except OSError:
                pass
            for file in files:
                print (file.filename)
                fileName = secure_filename(file.filename)
                file.save(os.path.join(userPath, fileName))
                crop_image(os.path.join(userPath, fileName))
            return redirect(url_for('home.home'))
            
    return render_template('images/upload.html')

def count_pngs():
    count = 0
    for file in os.listdir(current_app.config['UPLOAD_FOLDER']):
        if file.endswith(".png"):
            count += 1
    return count

@bp.route('/train', methods=['POST'])
@login_required
def train():
    #if enough images are present we want to trigger the image processing
    if(count_pngs() >= 5):
        if createTraining(g.user) :
            return "Training started", 200
        else:
            flash("Training already in process, please retry when the previous training has ended")
    else:
        flash("Not enough images to start training")


def sendTrainRequest():
    files = os.listdir(current_app.config['UPLOAD_FOLDER'])
    response = requests.post(url, files=files)
    return response.status_code
                                          

@bp.route('/display/<path:filename>')
@login_required
def display_image(filename):
    userPath = os.path.join(current_app.config['UPLOAD_FOLDER'], secure_filename(str(g.user['id'])))
    return send_from_directory(userPath, filename, as_attachment=True)
    
@bp.route('/delete/<path:filename>', methods=["POST"])
@login_required
def delete_image(filename):
    userPath = os.path.join(current_app.config['UPLOAD_FOLDER'], secure_filename(str(g.user['id'])))
    file_path = os.path.join(userPath, filename)
    if os.path.isfile(file_path):
        os.remove(file_path)
        flash("File deleted!")
    else:
        flash("File not found!")
    return redirect(url_for('home.home'))

def crop_image(imagePath):
    image = Image.open(imagePath)
    width, height = image.size
    image = crop_center(image, min(width,height), min(width,height))
    image = image.resize((256,256))
    image.save(imagePath)


def crop_center(pil_img, crop_width, crop_height):
    img_width, img_height = pil_img.size
    return pil_img.crop(((img_width - crop_width) // 2,
                         (img_height - crop_height) // 2,
                         (img_width + crop_width) // 2,
                         (img_height + crop_height) // 2))
