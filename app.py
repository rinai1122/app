from flask import Flask, render_template, request, send_file, jsonify
import os
from werkzeug.utils import secure_filename
from PyPDF2 import PdfReader, PdfWriter
from pydub import AudioSegment
import shutil
import subprocess
import sys
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from STT.STT import transcribe_audio  # Import your audio transcription function


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
for folder in [UPLOAD_FOLDER, DOWNLOAD_FOLDER, AUDIO_FOLDER]:
    if not os.path.exists(folder):
        os.makedirs(folder)

# def process_pdf(pdf_path, mp3_path, output_pdf_path):
#     """For testing: just return the exact input PDF."""
#     try:
#         # Copy the input PDF to the output location without modification
#         shutil.copy(pdf_path, output_pdf_path)
#         return True
#     except Exception as e:
#         print(f"Error copying PDF: {e}")
#         return False


def process_pdf(pdf_path, mp3_path, output_pdf_path, temp_dir):
    """Process the audio file and create a PDF based on the transcription."""
    try:
        # Step 1: Transcribe the audio file
        transcription = transcribe_audio(model_size=r'..\STT\fp16_ft', input_audio=mp3_path, temp_dir=temp_dir)

        # Step 2: Create a text file from the transcription
        txt_file_path = os.path.join(temp_dir, 'transcription.txt')
        with open(txt_file_path, 'w') as txt_file:
            for item in transcription:
                # Assuming each item is a dictionary with a 'text' key
                txt_file.write(item.get('text', '') + '\n')

        # Step 3: Run the external script to generate JSON from the PDF and text file
        json_output_path = './with_sent_prac.json'  # Path for the output JSON
        command = [
            'python', './almunai/main.py',
            '--pdf_path', pdf_path,
            '--text_path', txt_file_path,
            '--save_path', json_output_path
        ]
        
        result = subprocess.run(command, capture_output=True, text=True)
        if result.returncode != 0:
            print(f"Error running external script: {result.stderr}")
            return False

        # Step 4: Optionally: Use json_output_path to create a PDF (implement as needed)
        # This would depend on how you want to generate the PDF from the JSON
        # generate_pdf_from_json(json_output_path, output_pdf_path)

        # Step 5: Copy the original PDF to the output path (if needed)
        shutil.copy(pdf_path, output_pdf_path)
        return True
        
    except Exception as e:
        print(f"Error processing PDF: {e}")
        return False


# Route to render the main page
@app.route('/')
def index():
    return render_template('index.html')

# Route to handle PDF and audio upload and processing
@app.route('/upload/process', methods=['POST'])
def upload_and_process():
    if 'pdf_file' not in request.files or 'audio_file' not in request.files:
        return jsonify({"message": "PDF or audio file missing"}), 400
    
    pdf_file = request.files['pdf_file']
    audio_file = request.files['audio_file']
    
    # Validate the PDF and audio file types
    if pdf_file.filename == '' or not pdf_file.filename.endswith('.pdf'):
        return jsonify({"message": "Invalid PDF file"}), 400
    if audio_file.filename == '' or not audio_file.filename.endswith(('.mp3', '.wav', '.m4a')):
        return jsonify({"message": "Invalid audio file"}), 400
    
    # Secure and save the uploaded files
    pdf_filename = secure_filename(pdf_file.filename)
    audio_filename = secure_filename(audio_file.filename)
    pdf_path = os.path.join(app.config['UPLOAD_FOLDER'], pdf_filename)
    audio_path = os.path.join(app.config['AUDIO_FOLDER'], audio_filename)
    
    pdf_file.save(pdf_path)
    audio_file.save(audio_path)
    
    # Output path for the processed PDF
    output_pdf_path = os.path.join(app.config['DOWNLOAD_FOLDER'], f"processed_{pdf_filename}")
    
    # Process the PDF and audio together
    if process_pdf(pdf_path, audio_path, output_pdf_path, './'):
        download_link = f"/download/{os.path.basename(output_pdf_path)}"
        return jsonify({"message": "PDF processed successfully", "download_link": download_link}), 200
    else:
        return jsonify({"message": "Error processing PDF"}), 500

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
