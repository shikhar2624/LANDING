from flask import Flask, render_template, Response
import cv2
import os
import sys


app = Flask(__name__)
camera = cv2.VideoCapture(0)

getFrames =None
def RegisterGetFramesFunc(func):
    global getFrames
    getFrames =func

@app.route('/')
def index():
    return render_template('index.html')

def generate_frames():  
    while True:
        success, frame = camera.read()
        if not success:
            break
        else:
    # print(type(frame)," frames")
            ret, buffer = cv2.imencode('.jpg', frame)
            frame = buffer.tobytes()
            yield (b'--frame\r\n'
                    b'Content-Type: image/jpeg\r\n\r\n' + frame + b'\r\n\r\n')

@app.route('/video_feed')
def video_feed():
    return Response(getFrames(), mimetype='multipart/x-mixed-replace; boundary=frame')

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=8000)
