import Client
import Processing
import Camera
import cv2


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

    while status < 3:
        image = Camera.get_image()
        Camera.show_image('original', image, STATUS_TEXT[status])

        STATUS_FUNC[status]()

        frame = Client.getNextFrameFromServer()
        if frame.any():
            Camera.show_image('game', frame)

        # space to continue
        if cv2.waitKey(1) == 32:
            if status == 2:
                Client.sendResetToServer()
            else:
                Client.sendNextPhaseToServer()
            status = (status + 1) % (len(STATUS_TEXT) - 1)

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
