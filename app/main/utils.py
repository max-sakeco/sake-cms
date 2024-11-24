import os
from flask import current_app
from werkzeug.utils import secure_filename
import uuid

ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif'}

def allowed_file(filename):
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

def save_image(file, filename):
    # Generate a unique filename to prevent overwrites
    filename = f"{uuid.uuid4()}_{secure_filename(filename)}"
    filepath = os.path.join(current_app.config['UPLOAD_FOLDER'], filename)
    file.save(filepath)
    return filename
