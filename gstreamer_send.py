import gi
gi.require_version('Gst', '1.0')
from gi.repository import Gst

# Initialize GStreamer
Gst.init(None)

# Create the pipeline
pipeline = Gst.parse_launch("v4l2src device=/dev/video0 ! image/jpeg,width=1280,height=720,framerate=30/1 ! rtpjpegpay ! udpsink host=192.168.0.58 port=8000")

# Start the pipeline
pipeline.set_state(Gst.State.PLAYING)

# Wait until error or EOS (End of Stream) occurs
bus = pipeline.get_bus()
msg = bus.timed_pop_filtered(Gst.CLOCK_TIME_NONE, Gst.MessageType.ERROR | Gst.MessageType.EOS)

# Parse the message
if msg:
    if msg.type == Gst.MessageType.ERROR:
        error, debug_info = msg.parse_error()
        print("Error received from element {}: {}".format(msg.src.get_name(), error))
        print("Debugging information: {}".format(debug_info))
    elif msg.type == Gst.MessageType.EOS:
        print("End of stream reached")

# Stop the pipeline
pipeline.set_state(Gst.State.NULL)
