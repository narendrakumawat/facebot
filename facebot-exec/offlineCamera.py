import Camera
import cv2

while (True):
    image = Camera.get_image_external()
    Camera.show_image('localhost',image,'test')
    if cv2.waitKey(1) & 0xFF == ord('q'):
        break

# When everything done, release the capture
cv2.destroyAllWindows()