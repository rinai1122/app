from flask import Flask, render_template, request, send_file
import os
from werkzeug.utils import secure_filename

app = Flask(__name__)

# Directory to temporarily store files
UPLOAD_FOLDER = 'uploads'
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

if not os.path.exists(UPLOAD_FOLDER):
    os.makedirs(UPLOAD_FOLDER)

def return_pdf(file_path):
    return file_path

@app.route('/')
def index():
    return render_template('index.html')  # Render HTML form for uploading PDF

@app.route('/upload', methods=['POST'])
def upload_file():
    if 'file' not in request.files:
        return "No file part", 400
    file = request.files['file']
    
    if file.filename == '':
        return "No selected file", 400

    if file and file.filename.endswith('.pdf'):
        filename = secure_filename(file.filename)
        file_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
        file.save(file_path)

        # Call your return_pdf function on the uploaded file
        output_pdf_path = return_pdf(file_path)

        # Return the processed PDF as a downloadable file
        return send_file(output_pdf_path, as_attachment=True)

    return "File is not a PDF", 400

if __name__ == '__main__':
    app.run(debug=True)
