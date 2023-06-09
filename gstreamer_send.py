import gi
gi.require_version('Gst', '1.0')
from gi.repository import Gst

# Initialize GStreamer
Gst.init(None)

# Create the pipeline
pipeline = Gst.parse_launch("v4l2src device=/dev/video0 ! image/jpeg,width=1280,height=720,framerate=30/1 ! rtpjpegpay ! udpsink host=192.168.0.58 port=8000")

# Start the pipeline
pipeline.set_state(Gst.State.PLAYING)

try:
    # Run the pipeline
    while True:
        pass

except KeyboardInterrupt:
    pass

# Stop the pipeline
pipeline.set_state(Gst.State.NULL)
