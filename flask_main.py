from flask import Flask, render_template, Response
import cv2
import os
import sys
import memcache   ##for common sharing memory

##initialising memcache client
memc3=memcache.Client(['127.0.0.1:11211'],debug=1)

app = Flask(__name__)
camera = cv2.VideoCapture(0)

@app.route('/')
def index():
    return render_template('index.html')

def generate_frames():  
    while True:
        # success, frame = camera.read()
        data=memc3.get_multi(['ret','live_frame'])
        print(data)
        success=data['ret']

        if not success:
            break
        else:
            ret, buffer = cv2.imencode('.jpg', data['live_frame'])
            frame = buffer.tobytes()
            yield (b'--frame\r\n'
                    b'Content-Type: image/jpeg\r\n\r\n' + frame + b'\r\n\r\n')

@app.route('/video_feed')
def video_feed():
    return Response(generate_frames(), mimetype='multipart/x-mixed-replace; boundary=frame')

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=8000)
