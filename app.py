from flask import Flask, render_template, request, send_from_directory
import os
from werkzeug.utils import secure_filename
from video_processor import modify_video
import uuid

app = Flask(__name__)
UPLOAD_FOLDER = 'static/output'
OVERLAY_FOLDER = 'static/overlays'
ALLOWED_EXTENSIONS = {'mp4'}

os.makedirs(UPLOAD_FOLDER, exist_ok=True)
os.makedirs(OVERLAY_FOLDER, exist_ok=True)

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

@app.route("/", methods=["GET", "POST"])
def index():
    processed_files = []
    if request.method == "POST":
        if 'files' not in request.files:
            return "Aucun fichier fourni.", 400

        files = request.files.getlist("files")
        for file in files:
            if file and allowed_file(file.filename):
                filename = secure_filename(file.filename)
                unique_id = uuid.uuid4().hex[:8]
                saved_path = os.path.join(UPLOAD_FOLDER, f"{unique_id}_{filename}")
                file.save(saved_path)

                try:
                    output_path = modify_video(saved_path, UPLOAD_FOLDER, OVERLAY_FOLDER)
                    processed_filename = os.path.basename(output_path)
                    processed_files.append(processed_filename)
                except Exception as e:
                    print(f"Erreur pendant le traitement de {filename} : {e}")
                    continue

        return render_template("index.html", processed_files=processed_files)

    return render_template("index.html", processed_files=None)

@app.route("/download/<filename>")
def download_file(filename):
    return send_from_directory(UPLOAD_FOLDER, filename, as_attachment=True)
