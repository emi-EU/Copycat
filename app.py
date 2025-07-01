from flask import Flask, request, send_file, send_from_directory
import os
import tempfile
import subprocess
from werkzeug.utils import secure_filename

app = Flask(__name__)
UPLOAD_FOLDER = tempfile.gettempdir()

@app.route('/')
def index():
    return send_from_directory('static', 'index.html')

@app.route('/process', methods=['POST'])
def process():
    video = request.files['video']
    watermark = request.form['watermark']
    opacity = request.form['opacity']
    border_color = request.form['borderColor']
    border_width = request.form['borderWidth']

    filename = secure_filename(video.filename)
    input_path = os.path.join(UPLOAD_FOLDER, filename)
    output_path = os.path.join(UPLOAD_FOLDER, "output.mp4")
    video.save(input_path)

    drawtext = f"drawtext=text='{watermark}':x=mod(x\\,w/5):y=mod(y\\,h/5):fontsize=24:fontcolor=white@{opacity}"
    drawbox = f"drawbox=0:0:iw:ih:{border_width}:{border_color}"

    try:
        subprocess.run([
            'ffmpeg', '-i', input_path,
            '-vf', f"{drawtext},{drawbox}",
            '-preset', 'ultrafast',
            '-y', output_path
        ], check=True)

        return send_file(output_path, mimetype='video/mp4')
    except subprocess.CalledProcessError as e:
        return f"Erreur FFmpeg: {e}", 500
    finally:
        if os.path.exists(input_path): os.remove(input_path)
        if os.path.exists(output_path): os.remove(output_path)

@app.route('/static/<path:path>')
def serve_static(path):
    return send_from_directory('static', path)

if __name__ == '__main__':
    app.run(host="0.0.0.0", port=5000)
