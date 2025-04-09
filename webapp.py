from flask import Flask, request, send_file
import cv2
import numpy as np
import os
import sys
from werkzeug.utils import secure_filename

app = Flask(__name__)
UPLOAD_FOLDER = "uploads"
PROCESSED_FOLDER = "processed"
os.makedirs(UPLOAD_FOLDER, exist_ok=True)
os.makedirs(PROCESSED_FOLDER, exist_ok=True)
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

def apply_clahe(image_path):
    image = cv2.imread(image_path)
    lab = cv2.cvtColor(image, cv2.COLOR_BGR2LAB)
    l, a, b = cv2.split(lab)
    
    clahe = cv2.createCLAHE(clipLimit=3.0, tileGridSize=(8, 8))
    l_clahe = clahe.apply(l)
    lab_clahe = cv2.merge((l_clahe, a, b))
    enhanced_img = cv2.cvtColor(lab_clahe, cv2.COLOR_LAB2BGR)
    
    processed_path = os.path.join(PROCESSED_FOLDER, "enhanced.png")
    cv2.imwrite(processed_path, enhanced_img)
    return processed_path

@app.route('/', methods=['GET', 'POST'])
def upload_file():
    if request.method == 'POST':
        if 'file' not in request.files:
            return "No file part"
        file = request.files['file']
        if file.filename == '':
            return "No selected file"
        if file:
            filename = secure_filename(file.filename)
            filepath = os.path.join(app.config['UPLOAD_FOLDER'], filename)
            file.save(filepath)
            processed_path = apply_clahe(filepath)
            return send_file(processed_path, mimetype='image/png')

    return """
    <!doctype html>
    <html>
    <head>
        <title>Upload Image</title>
        <style>
            body {
                background-color: lightblue;
                text-align: center;
                font-family: Arial, sans-serif;
            }
            form {
                margin-top: 20px;
            }
            input[type="file"], input[type="submit"] {
                margin: 10px;
                padding: 10px;
            }
        </style>
    </head>
    <body>
        <h1>UPLOAD AN UNDERWATER IMAGE TO ENHANCE</h1>
        <form method="post" enctype="multipart/form-data">
            <input type="file" name="file">
            <input type="submit" value="Upload">
        </form>
    </body>
    </html>
    """

if __name__ == '__main__':
    port = int(os.environ.get("PORT", 5000))  # Use Render-assigned port
    app.run(host='0.0.0.0', port=port)
