import Client
import Processing
import Camera
import cv2

import DetectBlackPixels
import PaperHomography
from pyimagesearch import imutils


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
        # image = Camera.get_image()
        image = cv2.imread('IMG_9980.JPG')
        image = imutils.resize(image, height=480, width=640)
        M = cv2.getRotationMatrix2D((image.shape[1] / 2, image.shape[0] / 2), 270, 1)
        image = cv2.warpAffine(image, M, (image.shape[1], image.shape[0]))
        # Camera.show_image('original', image, STATUS_TEXT[status])

        # STATUS_FUNC[status](image)
        frame = Client.getNextFrameFromServer()
        if frame.any():
            # Camera.show_image('game', frame)

            points = PaperHomography.getPaperPoints(image)

            # apply the four point transform to obtain a top-down
            # view of the original image
            pointAsTuple = PaperHomography.arrayToTuple(points)
            paperSize = PaperHomography.paperSizer(sorted(pointAsTuple))
            paperSizes = (paperSize[1], paperSize[2])
            scannedInk = PaperHomography.scanInkFromImage(image, points)

            # show the original and scanned images
            # print "STEP 3: Apply perspective transform"
            paperImage = PaperHomography.implantFrameOnPaper(image, frame, paperSizes, pointAsTuple)
            cv2.imshow("Homogriphied", imutils.resize(paperImage))

        # space to continue
        if cv2.waitKey(1) == 32:
            if status == 0:
                lines = DetectBlackPixels.findBlackLines(imutils.resize(scannedInk, height=640, width=480))

                for line in lines:
                    if line != []:
                        Client.sendLineToServer(line)

            elif status == 2:
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
