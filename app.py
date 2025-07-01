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
    video = request.files.get('video')
    watermark = request.form.get('watermark')
    opacity = request.form.get('opacity')
    border_color = request.form.get('borderColor')
    border_width = request.form.get('borderWidth')

    # Logs de debug
    print("WATERMARK:", watermark)
    print("OPACITY:", opacity)
    print("BORDER COLOR:", border_color)
    print("BORDER WIDTH:", border_width)

    if not all([video, watermark, opacity, border_color, border_width]):
        return "Erreur : champs manquants", 400

    filename = secure_filename(video.filename)
    input_path = os.path.join(UPLOAD_FOLDER, filename)
    output_path = os.path.join(UPLOAD_FOLDER, "output.mp4")
    video.save(input_path)

    # Ajout du chemin vers la police Montserrat Bold
    font_path = os.path.abspath("fonts/Montserrat-Bold.ttf")

    drawtext = (
        f"drawtext=fontfile='{font_path}':"
        f"text='{watermark}':x=mod(x\\,w/5):y=mod(y\\,h/5):"
        f"fontsize=24:fontcolor=white@{opacity}"
    )
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
        print("FFmpeg error output:", e)
        return f"Erreur FFmpeg: {str(e)}", 500
    finally:
        if os.path.exists(input_path): os.remove(input_path)
        if os.path.exists(output_path): os.remove(output_path)

@app.route('/static/<path:path>')
def serve_static(path):
    return send_from_directory('static', path)

if __name__ == '__main__':
    app.run(host="0.0.0.0", port=5000, debug=True)
