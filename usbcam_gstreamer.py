import cv2
import gi
gi.require_version('Gst', '1.0')
from gi.repository import Gst, GObject

# Initialize GStreamer
Gst.init(None)

# Create the pipeline
pipeline = Gst.parse_launch("appsrc name=source ! videoconvert ! video/x-raw,format=BGR ! videoconvert ! "
                            "image/jpeg,framerate=30/1 ! rtpjpegpay ! "
                            "tee name=t ! queue ! udpsink host=$myip1 port=$myport1 t. ! queue ! udpsink host=$myip2 port=$myport2")

# Start the pipeline
pipeline.set_state(Gst.State.PLAYING)

# Create a GStreamer appsrc element
source = pipeline.get_by_name("source")
source.set_property("format", Gst.Format.TIME)

# Open the camera
cap = cv2.VideoCapture(0)

try:
    while True:
        ret, frame = cap.read()
        if not ret:
            break

        # Convert the OpenCV frame to a GStreamer buffer
        data = frame.tobytes()
        buffer = Gst.Buffer.new_allocate(None, len(data), None)
        buffer.fill(0, data)

        # Set the timestamp and duration for the buffer
        timestamp = Gst.util_get_timestamp()
        buffer.pts = buffer.dts = timestamp
        buffer.duration = int(1e9 / 30)

        # Push the buffer to the appsrc element
        source.emit("push-buffer", buffer)

        # Check for keyboard interrupt
        if cv2.waitKey(1) & 0xFF == ord('q'):
            break

except KeyboardInterrupt:
    pass

# Stop the pipeline
pipeline.set_state(Gst.State.NULL)

# Release the camera and close OpenCV windows
cap.release()
cv2.destroyAllWindows()
