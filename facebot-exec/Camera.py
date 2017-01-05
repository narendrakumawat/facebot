import cv2

# Initialize the camera capture object with the cv2.VideoCapture class.
# All it needs is the index to a camera port.
camera = cv2.VideoCapture(0)
camera.set(3,640)
camera.set(4,480)
rows = 0
cols = 0

# Captures a single image from the camera and returns it in PIL format
def get_image():
    # read is the easiest way to get a full image out of a VideoCapture object.
    retval, im = camera.read()
    return im

def show_image(windowName, image):
    cv2.imshow(windowName, image)