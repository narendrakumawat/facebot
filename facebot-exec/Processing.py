import DetectBlackPixels
import PaperHomography
import SyncGlobals

running = True

def isValidRect(paperPoints):
    for i in range (0,4):
        for j in range (i + 1,4):
            if (DetectBlackPixels.linearDistance(paperPoints[i],paperPoints[j]) < 50):
                return False
    return True

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

def processFrame(camImage):
    lastPaperPoints = SyncGlobals.getPaperPoints()
    newPaperPoints = PaperHomography.getPaperPoints(camImage)
    pointAsTuple = None
    paperPoints = None

    if newPaperPoints is not None and isValidRect(newPaperPoints):
        # apply the four point transform to obtain a top-down
        # view of the original image
        if lastPaperPoints is not None:
            if not isDifferentRectangle(lastPaperPoints, newPaperPoints):
                SyncGlobals.setPaperPoints(newPaperPoints)
                paperPoints = newPaperPoints
            else:
                paperPoints = lastPaperPoints
        else:
            paperPoints = newPaperPoints
        pointAsTuple = PaperHomography.arrayToTuple(paperPoints)

    elif lastPaperPoints is not None:
        pointAsTuple = PaperHomography.arrayToTuple(lastPaperPoints)

    if pointAsTuple is not None:
        SyncGlobals.setPointAsTuple(pointAsTuple)

        paperSize = PaperHomography.paperSizer(sorted(pointAsTuple))
        paperSizes = (paperSize[1], paperSize[2])
        SyncGlobals.setPaperSizes(paperSizes)

    if paperPoints is not None:
        scannedInk = PaperHomography.scanInkFromImage(camImage, paperPoints)
        SyncGlobals.setScannedInk(scannedInk)


def processingLoop():
    while running:
        camFrame = SyncGlobals.getCamFrame()

        if camFrame is not None:
            processFrame(camFrame)

    print 'Done Processing'

