import threading


camFrameLock = threading.Lock()
camFrame = None

def getCamFrame():
    camFrameLock.acquire()
    res = camFrame
    camFrameLock.release()
    return res

def setCamFrame(frame):
    global camFrame
    camFrameLock.acquire()
    camFrame = frame
    camFrameLock.release()


gameFrameLock = threading.Lock()
gameFrame = None

def getGameFrame():
    gameFrameLock.acquire()
    res = gameFrame
    gameFrameLock.release()
    return res

def setGameFrame(frame):
    global gameFrame
    gameFrameLock.acquire()
    gameFrame = frame
    gameFrameLock.release()


paperPointsLock = threading.Lock()
paperPoints = None

def getPaperPoints():
    paperPointsLock.acquire()
    res = paperPoints
    paperPointsLock.release()
    return res

def setPaperPoints(points):
    global paperPoints
    paperPointsLock.acquire()
    paperPoints = points
    paperPointsLock.release()


paperSizesLock = threading.Lock()
paperSizes = None

def getPaperSizes():
    paperSizesLock.acquire()
    res = paperSizes
    paperSizesLock.release()
    return res

def setPaperSizes(sizes):
    global paperSizes
    paperSizesLock.acquire()
    paperSizes = sizes
    paperSizesLock.release()


scannedInkLock = threading.Lock()
scannedInk = None

def getScannedInk():
    scannedInkLock.acquire()
    res = scannedInk
    scannedInkLock.release()
    return res

def setScannedInk(scan):
    global scannedInk
    scannedInkLock.acquire()
    scannedInk = scan
    scannedInkLock.release()


pointAsTupleLock = threading.Lock()
pointAsTuple = None

def getPointAsTuple():
    pointAsTupleLock.acquire()
    res = pointAsTuple
    pointAsTupleLock.release()
    return res

def setPointAsTuple(point):
    global pointAsTuple
    pointAsTupleLock.acquire()
    pointAsTuple = point
    pointAsTupleLock.release()
