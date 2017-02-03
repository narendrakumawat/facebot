
# import the necessary packages
from pyimagesearch.transform import four_point_transform
from skimage.filters import threshold_adaptive
import numpy as np
import cv2

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
    return res

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

def isBlack(b, g, r):
    return b == 0 and g == 0 and r == 0

def isBackground(b, g, r):
    return b >= 240 and b < 256 and g >= 0 and g <= 10 and r >= 240 and r <= 256

def isWhiteish(b, g, r):
    return b > WHITE_THRESHOLD and g > WHITE_THRESHOLD and r > WHITE_THRESHOLD

def mergeImages(foreground, background):
    for x in xrange (0,foreground.shape[0]):
        for y in xrange (0, foreground.shape[1]):
            b = foreground.item(x, y, 0)
            g = foreground.item(x, y, 1)
            r = foreground.item(x, y, 2)

            #If pixel is not off or of backgroud, aply it on paper.
            if not (isBlack(b,g,r) or isBackground(b,g,r)):
                b1 = background.item(x, y, 0)
                g1 = background.item(x, y, 1)
                r1 = background.item(x, y, 2)

                #if pixel is not white in the frame, it means
                #something is obstructing the paper.
                #We want to put game frame only on the paper.
                if (isWhiteish(b1, g1, r1)):
                    background.itemset((x,y,0), b)
                    background.itemset((x,y,1), g)
                    background.itemset((x,y,2), r)
    return

def getPaperPoints(image):

    # convert the image to grayscale, blur it, and find edges
    # in the image
    gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
    gray = cv2.GaussianBlur(gray, (5, 5), 0)
    edged = cv2.Canny(gray, 75, 200)

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

def scanInkFromImage(image, paperPoints):
    # show the contour (outline) of the piece of paper

    # apply the four point transform to obtain a top-down
    # view of the original image
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
    # Resize image to paper size
    imageToImplant = cv2.resize(imageToImplant, paperSize)
    src = np.array(
        [[0, 0], [imageToImplant.shape[1] - 1, 0], [0, imageToImplant.shape[0] - 1], [imageToImplant.shape[1] - 1, imageToImplant.shape[0] - 1]],
        np.float32)
    pointAsTuple = sortPoints(pointAsTuple)
    dst = np.array([[pointAsTuple[0], pointAsTuple[1], pointAsTuple[2], pointAsTuple[3]]], np.float32)

    #Get the prespective of the paper(get the matrix and apply it on game frame)
    ret = cv2.getPerspectiveTransform(src, dst)
    imageToImplantPaperPerspective = cv2.warpPerspective(imageToImplant, ret, ((paperImage.shape[1], paperImage.shape[0])))

    #Merge the game frame and cam frame.
    mergeImages(imageToImplantPaperPerspective, paperImage)
    return paperImage