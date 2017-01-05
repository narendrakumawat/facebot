import cv2
import numpy as np
import threading
import math
import socket
import sys
import base64
from PIL import Image
from StringIO import StringIO




size = (640,480)
objectsFoundPixels = [[], [], []]
bases = []
pixelBool = [[False] * 640] * 480
rangeY = range(0,639)
rangeX = range(0,479)

def connectBlack(dot, image, num):
    if pixelBool[dot[0]][dot[1]]:
        return
    #print dot
    pixelBool[dot[0]][dot[1]] = True
    objectsFoundPixels[num].append(dot)
    for x in range(dot[0] - 1, dot[0] + 2):
        for y in range(dot[1] - 1, dot[1] + 2):
            if (x in rangeX and y in rangeY and
                        image.item(x,y) < 80 and pixelBool[x][y] == False and (x,y) != dot):
                connectBlack((x,y), image, num)


def findBlackDots(image, objectsFoundPixels):
    objectsFoundPixels = [[],[],[]]
    blackHighBoundary = 80
    rows = 640
    cols = 480
    result = []
    num = 0
    gray_image = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
    for i in xrange(cols):
        for j in xrange(rows):
            black = (gray_image.item(i, j))
            if (black < blackHighBoundary):
                result.append((i,j))
                if (num < 3):
                    connectBlack((i,j),gray_image, num)
                    if len(objectsFoundPixels[num]) < 30:
                        objectsFoundPixels[num] = []
                    if (objectsFoundPixels[num] != []):
                        bases.append((i,j))
                        num = num + 1
    return result

def linearDistance(dot1,dot2):
    return math.sqrt(math.pow((dot1[0] - dot2[0]),2) + math.pow((dot1[1] - dot2[1]),2))

def cmpLinearDistance1(dot1,dot2):
    return int(linearDistance(bases[0],dot1) - linearDistance(bases[0],dot2))

def cmpLinearDistance2(dot1,dot2):
    return int(linearDistance(bases[1],dot1) - linearDistance(bases[1],dot2))

def cmpLinearDistance3(dot1,dot2):
    return int(linearDistance(bases[2],dot1) - linearDistance(bases[2],dot2))
# Now we can initialize the camera capture object with the cv2.VideoCapture class.
# All it needs is the index to a camera port.
camera = cv2.VideoCapture(0)
camera.set(3,640)
camera.set(4,480)
rows = 0
cols = 0

# Captures a single image from the camera and returns it in PIL format
def get_image():
    # read is the easiest way to get a full image out of a VideoCapture object.
    retval, im = camera.read()
    return im


def highlightBlack(image, dots, color):
    for i in range(len(dots)):
        if (dots[i] != None):
            image.itemset((dots[i][0],dots[i][1], 0), color[0])
            image.itemset((dots[i][0],dots[i][1], 1), color[1])
            image.itemset((dots[i][0],dots[i][1], 2), color[2])
    return image


sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
server_address = ('localhost', 1337)
print >> sys.stderr, 'connecting to %s port %s' % server_address
sock.connect(server_address)

def sendToServer(objectsFoundPixels):
    for i in range(3):
        print >> sys.stderr, 'sending object number "%s"' % str(objectsFoundPixels[i])
        sock.sendall(str(objectsFoundPixels[i]) + "<EOL>")
    # sock.sendall("<NEXT>")
    pass


def isCorner(dot):
    foundOne = False
    for i in range(dot[0] - 1, dot[0] + 2):
        for j in range(dot[1] - 1, dot[1] + 2):
            if (pixelBool[i][j]):
                if (not(foundOne)):
                    foundOne = True
                else:
                    return False
    return True

def findCorner(dots):
    for dot in dots:
        if isCorner(dot):
            return dot

def findBases(line):
    if line != []:
        dot = findCorner(line)
        if dot != None:
            bases.append()
        print(bases)
n=0
while (True):
    n = n + 1
    image = get_image()
    cv2.imshow('vid', image)
    # if (n % 100 == 0):
    dots = findBlackDots(image, objectsFoundPixels)

    for i in range (0,3):
        if (objectsFoundPixels[i] != []):
            findBases(objectsFoundPixels[i])
            if (len(bases) > i):
                objectsFoundPixels[i] = sorted(objectsFoundPixels[i], cmpLinearDistance1)
    sendToServer(objectsFoundPixels)
    # newimage1 = highlightBlack(image, objectsFoundPixels[0], (0, 0, 150))
    # newimage1 = highlightBlack(image, objectsFoundPixels[1], (0, 150, 0))
    # newimage1 = highlightBlack(image, objectsFoundPixels[2], (150, 0, 0))
    # cv2.imshow('highlight1', newimage1)
    # print (str(findBlackDots(image)) + '\n')
    if cv2.waitKey(1) == 27:
        break  # esc to quit

                # cameraThread = threading.Thread(target=cameraThreadWork)
# cameraThread.start()