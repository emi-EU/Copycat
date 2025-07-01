import os
import uuid
import subprocess
from flask import Flask, request, jsonify, send_file

app = Flask(__name__)

UPLOAD_FOLDER = '/tmp'
ALLOWED_EXTENSIONS = {'mp4'}
FONT_PATH = 'app/fonts/Montserrat-Bold.ttf'  # Chemin vers ta police
WATERMARK_TEXT = '@meow'


def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS


@app.route('/process', methods=['POST'])
def process():
    if 'video' not in request.files:
        return jsonify({'error': 'No video file provided'}), 400

    file = request.files['video']
    if file.filename == '':
        return jsonify({'error': 'No selected file'}), 400

    if not allowed_file(file.filename):
        return jsonify({'error': 'Unsupported file type'}), 400

    input_filename = f"{uuid.uuid4()}.mp4"
    input_path = os.path.join(UPLOAD_FOLDER, input_filename)
    file.save(input_path)

    output_filename = f"output_{uuid.uuid4()}.mp4"
    output_path = os.path.join(UPLOAD_FOLDER, output_filename)

    # Personnalisation watermark
    opacity = 0.2
    border_width = 10
    border_color = "#ffffff"
    watermark = WATERMARK_TEXT
    font_path = FONT_PATH

    drawtext = (
        f"drawtext=fontfile='{font_path}':"
        f"text='{watermark}':"
        f"x=mod(x\\,w/5):y=mod(y\\,h/5):"
        f"fontsize=24:fontcolor=white:alpha={opacity}:"
        f"borderw=0"
    )
    drawbox = f"drawbox=0:0:iw:ih:{border_width}:{border_color}"

    try:
        subprocess.run([
            'ffmpeg', '-i', input_path,
            '-vf', f"{drawtext},{drawbox}",
            '-preset', 'ultrafast',
            '-y', output_path
        ], check=True)

        return send_file(output_path, as_attachment=True)

    except subprocess.CalledProcessError as e:
        return jsonify({'error': f"Erreur FFmpeg: {e}"}), 500


@app.route('/')
def home():
    return 'Service de watermark opérationnel.'


if __name__ == '__main__':
    app.run(debug=True)
