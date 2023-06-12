import cv2
import gi
gi.require_version('Gst', '1.0')
from gi.repository import Gst, GLib

# Initialize GStreamer
Gst.init(None)

# Create the pipeline
pipeline = Gst.parse_launch("appsrc name=source ! videoconvert ! video/x-raw,format=BGR ! videoconvert ! image/jpeg ! rtpjpegpay ! udpsink host=192.168.0.58 port=8000")

# Start the pipeline
pipeline.set_state(Gst.State.PLAYING)

# Get the appsrc element from the pipeline
source = pipeline.get_by_name('source')

try:
    # Run the pipeline
    while True:
        # Capture an OpenCV image
        ret, frame = cv2.VideoCapture(0).read()
        if not ret:
            break

        # Convert the OpenCV image to a GStreamer buffer
        # _, buffer = cv2.imencode('.jpeg', frame)
        data = frame.tostring()
        # gst_buffer = Gst.Buffer.new_allocate(None, len(buffer), None)
        gst_buffer = Gst.Buffer.new_allocate(None, len(data), None)
        # gst_buffer.fill(0, buffer.tobytes())
        gst_buffer.fill(0,data)


        # Feed the GStreamer buffer into the appsrc element
        source.emit('push-buffer', gst_buffer)

        # Wait for some time (e.g., 33 milliseconds for ~30 fps)
        GLib.timeout_add(33, GLib.MainLoop().quit)
        GLib.MainLoop().run()

except KeyboardInterrupt:
    pass

# Stop the pipeline
pipeline.set_state(Gst.State.NULL)
