import Client
import Processing
import Camera
import cv2

import DetectBlackPixels
import PaperHomography
from pyimagesearch import imutils

rectangle_threshold = 20
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


def centerOfRect(paperPoints):
    sumX = 0
    sumY = 0
    for i in range (0,len(paperPoints)):
        sumX += paperPoints[i][0]
        sumY += paperPoints[i][1]
    return (sumX / 4, sumY  / 4)


def isDifferentRectangle(lastPaperPoints, paperPoints):
    centerOfLast = centerOfRect(lastPaperPoints)
    centerOfThis = centerOfRect(paperPoints)
    return DetectBlackPixels.linearDistance(centerOfLast, centerOfThis) > 200
    pass


def isValidRect(paperPoints):
    for i in range (0,4):
        for j in range (i + 1,4):
            if (DetectBlackPixels.linearDistance(paperPoints[i],paperPoints[j]) < 50):
                return False
    return True


def gameLoop():
    status = 0
    lastPaperPoints = None
    scannedInk = None

    while status < 3:
        # image = Camera.get_image()
        paperImage = Camera.get_image_external()
        paperImage = cv2.flip(paperImage,1)
        paperImage = imutils.resize(paperImage, height=480, width=640)
        # Camera.show_image('original', image, STATUS_TEXT[status])

        # STATUS_FUNC[status](image)
        frame = Client.getNextFrameFromServer()
        if frame.any():
            # Camera.show_image('game', frame)

            paperPoints = PaperHomography.getPaperPoints(paperImage)
            # print str(paperPoints) + "HEREHREHRER"
            pointAsTuple = None
            if (paperPoints != None and isValidRect(paperPoints)):
                # apply the four point transform to obtain a top-down
                # view of the original image
                if (lastPaperPoints != None):
                    if (not isDifferentRectangle(lastPaperPoints, paperPoints)):
                        lastPaperPoints = paperPoints
                    else:
                        paperPoints = lastPaperPoints
                pointAsTuple = PaperHomography.arrayToTuple(paperPoints)
                lastPaperPoints = paperPoints
            elif lastPaperPoints != None:
                pointAsTuple = PaperHomography.arrayToTuple(lastPaperPoints)

            if pointAsTuple != None:
                paperSize = PaperHomography.paperSizer(sorted(pointAsTuple))
                paperSizes = (paperSize[1], paperSize[2])
                #
                # print str(lastPoints) + "KKK"
                # if lastPoints[0] > 0 and lastPoints[1] > 0:
                scannedInk = PaperHomography.scanInkFromImage(paperImage, lastPaperPoints)

                # show the original and scanned images
                # print "STEP 3: Apply perspective transform"
                paperImage = PaperHomography.implantFrameOnPaper(paperImage, frame, paperSizes, pointAsTuple)

            cv2.imshow("Homogriphied", imutils.resize(paperImage))

        # space to continue
        if cv2.waitKey(1) == 32:
            if status == 0:
                if scannedInk != None:
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
