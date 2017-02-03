import DetectBlackPixels
import PaperHomography
import SyncGlobals

running = True

# Confirm passed points are corners of a large enough rectangle
def isValidRect(paperPoints):
    for i in range (0,4):
        for j in range (i + 1,4):
            if (DetectBlackPixels.linearDistance(paperPoints[i],paperPoints[j]) < 50):
                return False
    return True

# Find the center point of the passed rectangle corners
def centerOfRect(paperPoints):
    sumX = 0
    sumY = 0
    for i in range (0,len(paperPoints)):
        sumX += paperPoints[i][0]
        sumY += paperPoints[i][1]
    return (sumX / 4, sumY  / 4)

# Check if passed rectangles are in sufficiently different positions by comparing the center points
def isDifferentRectangle(lastPaperPoints, paperPoints):
    centerOfLast = centerOfRect(lastPaperPoints)
    centerOfThis = centerOfRect(paperPoints)
    return DetectBlackPixels.linearDistance(centerOfLast, centerOfThis) > 200

# Process current frame and cache data in thread-safe globals
def processFrame():
    camFrame = SyncGlobals.getCamFrame()

    if camFrame is not None:
        # init variables
        lastPaperPoints = SyncGlobals.getPaperPoints()
        newPaperPoints = PaperHomography.getPaperPoints(camFrame)
        pointAsTuple = None
        paperPoints = None

        # a valid rectangle was recognized in the current frame
        if newPaperPoints is not None and isValidRect(newPaperPoints):
            # apply the four point transform to obtain a top-down
            # view of the original image
            if lastPaperPoints is not None:
                if not isDifferentRectangle(lastPaperPoints, newPaperPoints):
                    # cache and work with new paper position
                    SyncGlobals.setPaperPoints(newPaperPoints)
                    paperPoints = newPaperPoints
                else:
                    # work with last paper position from cache
                    paperPoints = lastPaperPoints
            else:
                # on first capture, work with new paper position
                paperPoints = newPaperPoints

            pointAsTuple = PaperHomography.arrayToTuple(paperPoints)

        # a valid rectangle was not recognized, but one is already in cache
        elif lastPaperPoints is not None:
            pointAsTuple = PaperHomography.arrayToTuple(lastPaperPoints)

        # valid rectangle exists
        if pointAsTuple is not None:
            SyncGlobals.setPointAsTuple(pointAsTuple)

            # compute paper sizes
            paperSize = PaperHomography.paperSizer(sorted(pointAsTuple))
            paperSizes = (paperSize[1], paperSize[2])
            SyncGlobals.setPaperSizes(paperSizes)

        # valid rectangle exists
        if paperPoints is not None:
            # cache current paper as full frame
            scannedInk = PaperHomography.scanInkFromImage(camFrame, paperPoints)
            SyncGlobals.setScannedInk(scannedInk)

# Keep processing frames until shutdown
def processingLoop():
    while running:
        processFrame()

    print 'Done Processing'

