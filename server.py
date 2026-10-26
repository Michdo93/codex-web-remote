import subprocess
from flask import Flask, Response, render_template_string, request

app = Flask(__name__)

# Crop & Viewport Settings for Codex UI
CROP_W = 900
CROP_H = 750
OFFSET_X = 300
OFFSET_Y = 50

HTML_LAYOUT = """
<!DOCTYPE html>
<html lang="de">
<head>
    <meta charset="UTF-8">
    <title>Codex Remote</title>
    <style>
        html, body {
            margin: 0;
            padding: 0;
            width: 100%;
            height: 100%;
            overflow: hidden;
            background-color: #121212;
            display: flex;
            justify-content: center;
            align-items: center;
        }
        .stream-container {
            width: 100vw;
            height: 100vh;
            display: flex;
            justify-content: center;
            align-items: center;
        }
        img {
            max-width: 100%;
            max-height: 100%;
            object-fit: contain;
            cursor: pointer;
            display: block;
        }
    </style>
</head>
<body>
    <div class="stream-container">
        <img id="stream" src="/stream" alt="Codex UI">
    </div>
    <script>
        const img = document.getElementById('stream');
        img.addEventListener('click', (e) => {
            const rect = img.getBoundingClientRect();
            const scaleX = """ + str(CROP_W) + """ / rect.width;
            const scaleY = """ + str(CROP_H) + """ / rect.height;
            const clickX = Math.round((e.clientX - rect.left) * scaleX) + """ + str(OFFSET_X) + """;
            const clickY = Math.round((e.clientY - rect.top) * scaleY) + """ + str(OFFSET_Y) + """;

            fetch('/api/click', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ x: clickX, y: clickY })
            });
        });

        document.addEventListener('keydown', (e) => {
            if (e.key.length === 1 || e.key === 'Enter' || e.key === 'Backspace') {
                e.preventDefault();
                fetch('/api/type', {
                    method: 'POST',
                    headers: { 'Content-Type': 'application/json' },
                    body: JSON.stringify({ key: e.key })
                });
            }
        });
    </script>
</body>
</html>
"""

@app.route('/')
def index():
    return render_template_string(HTML_LAYOUT)

def generate_stream():
    cmd = [
        'ffmpeg',
        '-f', 'x11grab',
        '-video_size', '1280x800',
        '-i', ':99',
        '-vf', f'crop={CROP_W}:{CROP_H}:{OFFSET_X}:{OFFSET_Y}',
        '-r', '15',
        '-f', 'mpjpeg',
        '-'
    ]
    process = subprocess.Popen(cmd, stdout=subprocess.PIPE, stderr=subprocess.DEVNULL)
    try:
        while True:
            data = process.stdout.read(1024 * 16)
            if not data:
                break
            yield data
    finally:
        process.kill()

@app.route('/stream')
def stream():
    return Response(generate_stream(), mimetype='multipart/x-mixed-replace; boundary=ffmpeg')

@app.route('/api/click', methods=['POST'])
def click():
    data = request.json
    x, y = data['x'], data['y']
    subprocess.run(['xdotool', 'mousemove', str(x), str(y), 'click', '1'], env={'DISPLAY': ':99'})
    return ('', 204)

@app.route('/api/type', methods=['POST'])
def type_key():
    data = request.json
    key = data['key']
    if key == 'Enter':
        subprocess.run(['xdotool', 'key', 'Return'], env={'DISPLAY': ':99'})
    elif key == 'Backspace':
        subprocess.run(['xdotool', 'key', 'BackSpace'], env={'DISPLAY': ':99'})
    else:
        subprocess.run(['xdotool', 'type', key], env={'DISPLAY': ':99'})
    return ('', 204)

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=8080)
