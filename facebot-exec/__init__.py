import Client
import DetectBlackPixels
import Camera
import cv2

Client.start()

while (True):
    image = Camera.get_image()
    Camera.show_image('original', image)

    lines = DetectBlackPixels.findBlackLines(image)
    highlight = DetectBlackPixels.highlightBlack(image, lines[0], (255, 0, 0))
    # Camera.show_image('highlight', highlight)

    for line in lines:
        if line != []:
            Client.sendLineToServer(line)

    frame = Client.sendNextToServer()
    if frame.any():
        Camera.show_image('game', frame)

    if cv2.waitKey(1) == 27:
        break  # esc to quit

cv2.destroyAllWindows()
Client.stop()
