# USAGE
# python PaperHomography.py --image images/page.jpg

# import the necessary packages
import threading

import pyimagesearch.transform as transform
from pyimagesearch.transform import four_point_transform
from skimage.filters import threshold_adaptive
import numpy as np
import cv2
import Utils
import Camera

backGroundTriplet = (255,0,255)
WHITE_THRESHOLD = 200


def find_corners(image):
    im = cv2.Canny(image, 100, 200)

    cnt = cv2.findContours(im,cv2.RETR_EXTERNAL,cv2.CHAIN_APPROX_SIMPLE)[0]
    cnt = cv2.approxPolyDP(cnt[0], 5, True)
    return cnt.astype(np.float32)

def arrayToTuple(arr):
    res = []
    for i in range (0,4):
        res.append([arr[i][0],arr[i][1]])
    # print res
    return res

def changePerspective(image, pts):
	# obtain a consistent order of the points and unpack them
	# individually
	rect = transform.order_points(pts)
	(tl, tr, br, bl) = rect

	# compute the width of the new image, which will be the
	# maximum distance between bottom-right and bottom-left
	# x-coordiates or the top-right and top-left x-coordinates
	widthA = np.sqrt(((br[0] - bl[0]) ** 2) + ((br[1] - bl[1]) ** 2))
	widthB = np.sqrt(((tr[0] - tl[0]) ** 2) + ((tr[1] - tl[1]) ** 2))
	maxWidth = max(int(widthA), int(widthB))

	# compute the height of the new image, which will be the
	# maximum distance between the top-right and bottom-right
	# y-coordinates or the top-left and bottom-left y-coordinates
	heightA = np.sqrt(((tr[0] - br[0]) ** 2) + ((tr[1] - br[1]) ** 2))
	heightB = np.sqrt(((tl[0] - bl[0]) ** 2) + ((tl[1] - bl[1]) ** 2))
	maxHeight = max(int(heightA), int(heightB))

	# now that we have the dimensions of the new image, construct
	# the set of destination points to obtain a "birds eye view",
	# (i.e. top-down view) of the image, again specifying points
	# in the top-left, top-right, bottom-right, and bottom-left
	# order
	dst = np.array([
		[0, 0],
		[maxWidth - 1, 0],
		[maxWidth - 1, maxHeight - 1],
		[0, maxHeight - 1]], dtype = "float32")

	# compute the perspective transform matrix and then apply it
	M = cv2.getPerspectiveTransform(rect, dst)
	warped = cv2.warpPerspective(image, M, (maxWidth, maxHeight))

	# return the warped image
	return warped

def getCorners(img):
     return np.array([(0,0), (0,img.shape[1] - 1), (img.shape[0] - 1,img.shape[1] - 1), (img.shape[0] - 1, 0)])

def paperSizer(points):
    topLeft = 0
    topRight = 0
    botLeft = 0
    botRight = 0
    if (points[0][1] <= points[1][1]):
        topLeft = points[0]
        topRight = points[1]
    else:
        topLeft = points[1]
        topRight = points[0]
    if (points[2][1] <= points[3][1]):
        botLeft = points[2]
        botRight = points[3]
    else:
        botLeft = points[3]
        botRight = points[2]
    height = abs(topLeft[0] - botLeft[0])
    width = abs(topLeft[1] - topRight[1])
    return (topLeft, height,width)

def getPaperOnly(image, grayImage):
    return image[150:260,140:480]

# Assume 2 pictures are of same size.
def isBlack(b, g, r):
    return b == 0 and g == 0 and r == 0


def isBackground(b, g, r):
    return (b,g,r) == backGroundTriplet

def isWhiteish(b, g, r):
    return b > WHITE_THRESHOLD and g > WHITE_THRESHOLD and r > WHITE_THRESHOLD


def mergeImages(foreground, background):
    # class merger(threading.Thread):
    #     def __init__(self, threadID, foreground, background, x, y):
    #         threading.Thread.__init__(self)
    #         self.threadID = threadID
    #         self.foreground = foreground
    #         self.background = background
    #         self.x = x
    #         self.y = y
    #
    #     def run(self):
    #         # print "Starting " + self.name
    #         for x in range(self.x, self.x + 240):
    #             for y in range(self.y, self.y+ 320):
    #                 b = self.foreground.item(x, y, 0)
    #                 g = self.foreground.item(x, y, 1)
    #                 r = self.foreground.item(x, y, 2)
    #                 if not (isBlack(b, g, r) or isBackground(b, g, r)):
    #                     b1 = self.background.item(x, y, 0)
    #                     g1 = self.background.item(x, y, 1)
    #                     r1 = self.background.item(x, y, 2)
    #                     if (isWhiteish(b1, g1, r1)):
    #                         self.background.itemset((x, y, 0), b)
    #                         self.background.itemset((x, y, 1), g)
    #                         self.background.itemset((x, y, 2), r)
    #         return
    # print str(topLeft) + "YOROYORO" + str(size)
    # # (255,0,255)
    # merger1 = merger(0,foreground,background,0,0)
    # merger2 = merger(1,foreground,background,240,0)
    # merger3 = merger(2,foreground,background,0,320)
    # merger4 = merger(3,foreground,background,240,320)
    # merger1.start()
    # merger2.start()
    # merger3.start()
    # merger4.start()
    # merger1.join()
    # merger2.join()
    # merger3.join()
    # merger4.join()
    for x in xrange (0,foreground.shape[0]):
        for y in xrange (0, foreground.shape[1]):
            b = foreground.item(x, y, 0)
            g = foreground.item(x, y, 1)
            r = foreground.item(x, y, 2)
            if not (isBlack(b,g,r) or isBackground(b,g,r)):
                b1 = background.item(x, y, 0)
                g1 = background.item(x, y, 1)
                r1 = background.item(x, y, 2)
                if (isWhiteish(b1, g1, r1)):
                    background.itemset((x,y,0), b)
                    background.itemset((x,y,1), g)
                    background.itemset((x,y,2), r)
    return

def findTopLeft(tuples):
    minX = 10000
    minY = 10000
    for i in xrange (0,len(tuples)):
        if tuples[i][0] < minX: minX = tuples[i][0]
        if tuples[i][1] < minY: minY = tuples[i][1]
    return (minX, minY)

def getPaperPoints(image):

    # convert the image to grayscale, blur it, and find edges
    # in the image
    gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
    gray = cv2.GaussianBlur(gray, (5, 5), 0)
    edged = cv2.Canny(gray, 75, 200)

    # show the original image and the edge detected image
    # print "STEP 1: Edge Detection"

    # find the contours in the edged image, keeping only the
    # largest ones, and initialize the screen contour
    (cnts, _) = cv2.findContours(edged, cv2.RETR_LIST, cv2.CHAIN_APPROX_SIMPLE)
    cnts = sorted(cnts, key=cv2.contourArea, reverse=True)[:5]

    # loop over the contours
    for c in cnts:
        # approximate the contour
        peri = cv2.arcLength(c, True)
        approx = cv2.approxPolyDP(c, 0.02 * peri, True)

        # if our approximated contour has four points, then we
        # can assume that we have found our screen
        if len(approx) == 4:

            return approx.reshape(4,2)
            # Bublil: I added a flag here to avoid crashes when no rectangle in picture.
            # Also, screenCNT is a list of 4 points, representing the points of the rectangle.

def scanInkFromImage(image, paperPoints):
    # show the contour (outline) of the piece of paper
    # print "STEP 2: Find contours of paper"

    # apply the four point transform to obtain a top-down
    # view of the original image
    # print paperPoints
    warped = four_point_transform(image, paperPoints)
    tuples = arrayToTuple(paperPoints)
    paperSize = paperSizer(sorted(tuples))
    # convert the warped image to grayscale, then threshold it
    # to give it that 'black and white' paper effect
    warped = cv2.cvtColor(warped, cv2.COLOR_BGR2GRAY)
    warped = threshold_adaptive(warped, 251, offset=10)
    warped = warped.astype("uint8") * 255
    return warped


def sortPoints(pointAsTuple):
    res = [(0,0),(0,0),(0,0),(0,0)]
    for i in range (0,4):
        point = pointAsTuple[i]
        if (point[0] < 320):
            if (point[1] < 240):
                res[0] = point
            else:
                res[2] = point
        else:
            if (point[1] < 210):
                res[1] = point
            else:
                res[3] = point
    return res


def implantFrameOnPaper(paperImage, imageToImplant, paperSize, pointAsTuple):
    # show the original and scanned images
    # print "STEP 3: Apply perspective transform"
    # Resize image to paper size
    # print paperSize
    imageToImplant = cv2.resize(imageToImplant, paperSize)

    src = np.array(
        [[0, 0], [imageToImplant.shape[1] - 1, 0], [imageToImplant.shape[1] - 1, imageToImplant.shape[0] - 1], [0, imageToImplant.shape[0] - 1]],
        np.float32)

    src = np.array(
        [[0, 0], [imageToImplant.shape[1] - 1, 0], [0, imageToImplant.shape[0] - 1], [imageToImplant.shape[1] - 1, imageToImplant.shape[0] - 1]],
        np.float32)
    pointAsTuple = sortPoints(pointAsTuple)
    dst = np.array([[pointAsTuple[0], pointAsTuple[1], pointAsTuple[2], pointAsTuple[3]]], np.float32)
    ret = cv2.getPerspectiveTransform(src, dst)
    imageToImplantPaperPerspective = cv2.warpPerspective(imageToImplant, ret, ((paperImage.shape[1], paperImage.shape[0])))
    mergeImages(imageToImplantPaperPerspective, paperImage)
    return paperImage














def runDemoStill():
    pikachu = cv2.imread('Pikachu.jpg')
    paperImage = cv2.imread(Utils.adjustPathToOS('C:\Users\dbublil\Desktop\ImagesFOrCBV\PaperVideo (1-16-2017 6-07-27 PM)\PaperVideo 11.jpg'))
    # paperImage = cv2.imread("IMG_9987.JPG")
    M = cv2.getRotationMatrix2D((paperImage.shape[1] / 2, paperImage.shape[0] / 2), 270, 1)
    paperImage = cv2.warpAffine(paperImage, M, (paperImage.shape[1], paperImage.shape[0]))
    paperImage = cv2.resize(paperImage, (480,640))
    points = getPaperPoints(paperImage)

    # apply the four point transform to obtain a top-down
    # view of the original image
    pointAsTuple = arrayToTuple(points)
    paperSize = paperSizer(sorted(pointAsTuple))
    paperSizes = (paperSize[1], paperSize[2])
    scannedInk = scanInkFromImage(paperImage,points)

    # show the original and scanned images
    # print "STEP 3: Apply perspective transform"
    paperImage = implantFrameOnPaper(paperImage,pikachu,paperSizes, pointAsTuple)
    cv2.imshow("Homogriphied", paperImage)
    cv2.imshow("Scanned", cv2.resize(scannedInk, (640,480)))
    # print "done"
    cv2.waitKey(0)

def runDemoVideo():
    pikachu = cv2.imread('Pikachu.jpg')
    path = Utils.adjustPathToOS("PaperVideo (1-16-2017 6-07-27 PM)\PaperVideo ")
    n = 1
    while (n < 50):
        n = n + 1
        curPath = path + str(n) + ".jpg"
        paperImage = cv2.imread(curPath)
        # M = cv2.getRotationMatrix2D((paperImage.shape[1] / 2, paperImage.shape[0] / 2), 270, 1)
        # paperImage = cv2.warpAffine(paperImage, M, (paperImage.shape[1], paperImage.shape[0]))
        paperImage = cv2.resize(paperImage, (480,640))
        points = getPaperPoints(paperImage)

        # apply the four point transform to obtain a top-down
        # view of the original image
        if (points != None):
            pointAsTuple = arrayToTuple(points)
            paperSize = paperSizer(sorted(pointAsTuple))
            paperSizes = (paperSize[1], paperSize[2])
            scannedInk = scanInkFromImage(paperImage,points)

            # show the original and scanned images
            # print "STEP 3: Apply perspective transform"
            paperImage = implantFrameOnPaper(paperImage,pikachu,paperSizes, pointAsTuple)
            cv2.imshow("Homogriphied", paperImage)
            if cv2.waitKey(1) & 0xFF == ord('q'):
                break
            # cv2.imshow("Scanned", imutils.resize(scannedInk, height=640, width=480))

def runDemoVideoCam():
    pikachu = cv2.imread('Pikachu.jpg')
    # path = Utils.adjustPathToOS("C:\Users\dbublil\Desktop\ImagesFOrCBV\PaperVideo (1-16-2017 6-07-27 PM)\PaperVideo ")
    # n = 1
    lastGoodFrame = None
    while (True):
        # n = n + 1
        # curPath = path + str(n) + ".jpg"
        paperImage = Camera.get_image_external()
        # M = cv2.getRotationMatrix2D((paperImage.shape[1] / 2, paperImage.shape[0] / 2), 270, 1)
        # paperImage = cv2.warpAffine(paperImage, M, (paperImage.shape[1], paperImage.shape[0]))
        paperImage = cv2.resize(paperImage, (480,640))
        points = getPaperPoints(paperImage)

        # apply the four point transform to obtain a top-down
        # view of the original image
        if (points != None):
            pointAsTuple = arrayToTuple(points)
            paperSize = paperSizer(sorted(pointAsTuple))
            paperSizes = (paperSize[1], paperSize[2])
            scannedInk = scanInkFromImage(paperImage,points)
            cv2.imshow("Ink",scannedInk)
            # show the original and scanned images
            # print "STEP 3: Apply perspective transform"
            paperImage = implantFrameOnPaper(paperImage,pikachu,paperSizes, pointAsTuple)
            lastGoodFrame = paperImage.copy()
        elif (lastGoodFrame != None):
            paperImage = lastGoodFrame
        cv2.imshow("Homogriphied", paperImage)
        if cv2.waitKey(1) & 0xFF == ord('q'):
            break
# cv2.imshow('cam',Camera.get_image_external())
# runDemoStill()
# runDemoVideo()
# runDemoVideoCam()

