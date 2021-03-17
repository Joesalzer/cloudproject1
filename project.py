import os
#from app import app
import urllib.request
from flask import Flask, flash, request, redirect, url_for, render_template, send_from_directory
from PIL import Image, ImageOps,ImageFilter
import boto3
from botocore.exceptions import ClientError

app = Flask(__name__)

ALLOWED_EXTENSIONS = set(['png', 'jpg', 'jpeg', 'gif'])
UPLOAD_FOLDER = 'static/uploads/'

def allowed_file(filename):
        return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

@app.route('/')
def upload_form():
	return render_template('upload.html')

@app.route('/', methods=['POST','GET'])
def upload_image():
        
        if "file" not in request.files:
                flash("No file part")
                return redirect(requests.url)
        
        try:
                preset = request.form.get("preset")
        except:
                flash("No preset part")
                return redirect(requests.url)

        file = request.files["file"]

        if file.filename == "":
                flash('No image selected for uploading')
                return redirect(request.url)
        if file and allowed_file(file.filename):
                #save originial image in upload folder
                filename = file.filename
                file.save(os.path.join(UPLOAD_FOLDER, filename))

                #save edited image in upload folder
                image = applyfilter(preset,filename)
                image.save(os.path.join(UPLOAD_FOLDER, 'temp.jpg'))
                
                return send_image("temp.jpg")
        else:
                flash('Allowed image types are -> png, jpg, jpeg, gif')
                return redirect(request.url)

def applyfilter(preset, filename):
        #open and process image
        target = os.path.join(UPLOAD_FOLDER)
        destination = "".join([target, filename])
        img = Image.open(destination)

        #check and applying preset
        if preset == "gray":
                img = ImageOps.grayscale(img)
        if preset == "edge":
                img = ImageOps.grayscale(img)
                img = img.filter(ImageFilter.FIND_EDGES)
        if preset == "poster":
                img = ImageOps.posterize(img,3)
        if preset == "solar":
                img = ImageOps.solarize(img, threshold=80)
        if preset=='blur':
                img = img.filter(ImageFilter.BLUR)
        if preset=='sepia':
                sepia = []
                r, g, b = (239, 224, 185)
                for i in range(255):
                        sepia.extend((int(r*i/255), int(g*i/255), int(b*i/255)))
                img = img.convert("L")
                img.putpalette(sepia)
                img = img.convert("RGB")

        return img

# retrieve file from 'static/images' directory
@app.route('/static/uploads/<filename>')
def send_image(filename):
        return send_from_directory("static/uploads", filename)

def upload_file(file_name, bucket, object_name=None):
    """Upload a file to an S3 bucket

    :param file_name: File to upload
    :param bucket: Bucket to upload to
    :param object_name: S3 object name. If not specified then file_name is used
    :return: True if file was uploaded, else False
    """

    # If S3 object_name was not specified, use file_name
    if object_name is None:
        object_name = file_name

    # Upload the file
    s3_client = boto3.client('s3')
    try:
        response = s3_client.upload_file(file_name, bucket, object_name)
    except ClientError as e:
        logging.error(e)
        return False
    return True


if __name__ == "__main__":
        app.run()
    
        
        
        
        
        




