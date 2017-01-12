import Client
import Processing
import Camera
import cv2
import DetectBlackPixels


STATUS_TEXT = [
    "Phase 0: draw lines",
    "Phase 1: play",
    "Phase 2: click space to restart"
]
STATUS_FUNC = [
    Processing.phase0DetectAndSendLines,
    Processing.phase1ProcessingFunc,
    Processing.phase2ProcessingFunc
]


def gameLoop():
    status = 0

    while True:
        image = Camera.get_image()
        Camera.show_image('original', image, STATUS_TEXT[status])

        # STATUS_FUNC[status](image)

        frame = Client.getNextFrameFromServer()
        if len(frame) > 0:
            Camera.show_image('game', frame, STATUS_TEXT[status])

        # space to continue
        if cv2.waitKey(1) == 32:
            Client.sendNextPhaseToServer()
            status = (status + 1) % len(STATUS_TEXT)

            if status == 1:
                lines = DetectBlackPixels.findBlackLines(image)

                for line in lines:
                    if line != []:
                        Client.sendLineToServer(line)

            elif status == 0:
                Client.sendResetToServer()

        # esc to quit
        if cv2.waitKey(1) == 27:
            Client.sendQuitToServer()
            break


def init():
    Client.start()

    gameLoop()

    cv2.destroyAllWindows()
    Client.stop()

init()
