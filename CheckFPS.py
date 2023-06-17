import cv2

## capturing camera feed
video=cv2.VideoCapture(0)

fps=video.get(cv2.CAP_PROP_FPS)

print(f'FPS is  {fps}')