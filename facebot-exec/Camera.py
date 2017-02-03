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
    retval, im = camera.read()
    return im

# Captures a single image from the external camera and returns it in PIL format
def get_image_external():
    if not externalCamera.isOpened():
        # fallback to standard camera
        return get_image()

    retval, im = externalCamera.read()
    return im

# Display the passed frame in a window, with the passed text on top
def show_image(windowName, image, statusText):
    font = cv2.FONT_HERSHEY_SIMPLEX
    cv2.putText(image, statusText, (30, 460), font, 0.75, (255, 255, 255), 2)

    cv2.imshow(windowName, image)