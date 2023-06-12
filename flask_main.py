from flask import Flask, render_template, Response
import cv2
import os
import sys

from main import aruco_tracker

app = Flask(__name__)
frame=aruco_tracker.live_frames
# camera = cv2.VideoCapture(0)
print(frame)

@app.route('/')
def index():
    return render_template('index.html')

def generate_frames():
    global frame  
    # while True:
    #     success, frame = camera.read()
    #     if not success:
    #         break
    #     else:
    ret, buffer = cv2.imencode('.jpg', frame)
    frame = buffer.tobytes()
    yield (b'--frame\r\n'
            b'Content-Type: image/jpeg\r\n\r\n' + frame + b'\r\n\r\n')

@app.route('/video_feed')
def video_feed():
    return Response(generate_frames(), mimetype='multipart/x-mixed-replace; boundary=frame')

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=8000)
