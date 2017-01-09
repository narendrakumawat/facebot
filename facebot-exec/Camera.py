import cv2

# Initialize the camera capture object with the cv2.VideoCapture class.
# All it needs is the index to a camera port.
camera = cv2.VideoCapture(0)
externalCamera = cv2.VideoCapture(1)
externalCamera.set(3,640)
externalCamera.set(4,480)
camera.set(3,640)
camera.set(4,480)
rows = 0
cols = 0

# Captures a single image from the camera and returns it in PIL format
def get_image():
    # read is the easiest way to get a full image out of a VideoCapture object.
    retval, im = camera.read()
    return im

def get_image_external():
    # read is the easiest way to get a full image out of a VideoCapture object.
    retval, im = externalCamera.read()
    return im

def show_image(windowName, image, statusText):
    font = cv2.FONT_HERSHEY_SIMPLEX
    cv2.putText(image, statusText, (10, 500), font, 1, (255, 0, 0), 2)

    cv2.imshow(windowName, image)