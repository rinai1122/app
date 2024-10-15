from flask import Flask, render_template, request, send_file, jsonify
import os
from werkzeug.utils import secure_filename

app = Flask(__name__)

# Directory to temporarily store files
UPLOAD_FOLDER = 'uploads'
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

# Directory to store downloadable files
DOWNLOAD_FOLDER = 'downloads'
app.config['DOWNLOAD_FOLDER'] = DOWNLOAD_FOLDER

# Directory to store audio files
AUDIO_FOLDER = 'audios'
app.config['AUDIO_FOLDER'] = AUDIO_FOLDER

# Create necessary folders if they don't exist
if not os.path.exists(UPLOAD_FOLDER):
    os.makedirs(UPLOAD_FOLDER)

if not os.path.exists(DOWNLOAD_FOLDER):
    os.makedirs(DOWNLOAD_FOLDER)

if not os.path.exists(AUDIO_FOLDER):
    os.makedirs(AUDIO_FOLDER)

def return_pdf(file_path):
    return file_path

@app.route('/')
def index():
    return render_template('index.html')

# Route to upload PDF files
@app.route('/upload/pdf', methods=['POST'])
def upload_pdf():
    if 'file' not in request.files:
        return jsonify({"message": "No file part"}), 400
    file = request.files['file']
    
    if file.filename == '':
        return jsonify({"message": "No selected file"}), 400

    if file and file.filename.endswith('.pdf'):
        filename = secure_filename(file.filename)
        file_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
        file.save(file_path)

        return jsonify({"message": "PDF uploaded and processed successfully."}), 200

    return jsonify({"message": "File is not a PDF"}), 400

# Route to upload audio files
@app.route('/upload/audio', methods=['POST'])
def upload_audio():
    if 'audio_file' not in request.files:
        return jsonify({"message": "No file part"}), 400
    file = request.files['audio_file']

    if file.filename == '':
        return jsonify({"message": "No selected file"}), 400

    if file and file.filename.endswith(('.mp3', '.wav')):
        filename = secure_filename(file.filename)
        file_path = os.path.join(app.config['AUDIO_FOLDER'], filename)
        file.save(file_path)

        return jsonify({"message": "Audio uploaded and processed successfully."}), 200

    return jsonify({"message": "File is not an audio file"}), 400

# Route to download files
@app.route('/download/<filename>', methods=['GET'])
def download_file(filename):
    file_path = os.path.join(app.config['DOWNLOAD_FOLDER'], filename)
    
    if os.path.exists(file_path):
        return send_file(file_path, as_attachment=True)
    else:
        return "File not found", 404

if __name__ == '__main__':
    app.run(debug=True)
