# USAGE
# python PaperHomography.py --image images/page.jpg

# import the necessary packages
from pyimagesearch.transform import four_point_transform
from pyimagesearch import imutils
from skimage.filters import threshold_adaptive
import numpy as np
import argparse
import cv2

# construct the argument parser and parse the arguments
# ap = argparse.ArgumentParser()
# ap.add_argument("-i", "--image", required = True,
# 	help = "Path to the image to be scanned")
# args = vars(ap.parse_args())

# load the image and compute the ratio of the old height
# to the new height, clone it, and resize it
camera = cv2.VideoCapture(0)
for i in range(0, 10):
    camera.read()
pikachu = cv2.imread('Pikachu.jpg')

def find_corners(image):
    im = cv2.Canny(image, 100, 200)

    cnt = cv2.findContours(im,cv2.RETR_EXTERNAL,cv2.CHAIN_APPROX_SIMPLE)[0]
    cnt = cv2.approxPolyDP(cnt[0], 5, True)
    return cnt.astype(np.float32)

def arrayToTuple(arr):
    res = []
    for i in range (0,4):
        res.append((arr[i][0],arr[i][1]))
    print res
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

while (True):
    ret, image = camera.read()
    image = cv2.imread('IMG_9980.JPG')
    rows, cols, color = image.shape

    # Rotate 90 degrees to the right
    M = cv2.getRotationMatrix2D((cols / 2, rows / 2), 270, 1)
    image = cv2.warpAffine(image, M, (cols, rows))

    # cv2.imshow('ga',image)
    ratio = image.shape[0] / 500.0
    orig = image.copy()
    image = imutils.resize(image, height=500)

    # convert the image to grayscale, blur it, and find edges
    # in the image
    gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
    gray = cv2.GaussianBlur(gray, (5, 5), 0)
    edged = cv2.Canny(gray, 75, 200)

    # show the original image and the edge detected image
    print "STEP 1: Edge Detection"
    # cv2.imshow("Orig", orig)
    cv2.imshow("Image", image)
    cv2.imshow("Edged", edged)
    cv2.waitKey(0)
    cv2.destroyAllWindows()

    # find the contours in the edged image, keeping only the
    # largest ones, and initialize the screen contour
    (cnts, _) = cv2.findContours(edged.copy(), cv2.RETR_LIST, cv2.CHAIN_APPROX_SIMPLE)
    cnts = sorted(cnts, key=cv2.contourArea, reverse=True)[:5]

    # loop over the contours
    flag = False
    for c in cnts:
        # approximate the contour
        peri = cv2.arcLength(c, True)
        approx = cv2.approxPolyDP(c, 0.02 * peri, True)

        # if our approximated contour has four points, then we
        # can assume that we have found our screen
        if len(approx) == 4:
            screenCnt = approx
            print "cnt" + str(screenCnt)
            # Bublil: I added a flag here to avoid crashes when no rectangle in picture.
			# Also, screenCNT is a list of 4 points, represnting the points of the rectangle.
            flag = True
            break

    if (flag):
        # show the contour (outline) of the piece of paper
        print "STEP 2: Find contours of paper"
        cv2.drawContours(image, [screenCnt], -1, (0, 255, 0), 2)
        cv2.imshow("Outline", image)
        cv2.waitKey(0)
        cv2.destroyAllWindows()

        # apply the four point transform to obtain a top-down
        # view of the original image
        warped = four_point_transform(orig, screenCnt.reshape(4, 2) * ratio)
        tuples = arrayToTuple(screenCnt.reshape(4,2))
        paperSize = paperSizer(sorted(tuples))
        print paperSize
        # convert the warped image to grayscale, then threshold it
        # to give it that 'black and white' paper effect
        warped = cv2.cvtColor(warped, cv2.COLOR_BGR2GRAY)
        warped = threshold_adaptive(warped, 251, offset=10)
        warped = warped.astype("uint8") * 255

        # show the original and scanned images
        print "STEP 3: Apply perspective transform"

        # Not perfect yet.
        pikachu = cv2.resize(pikachu,(paperSize[1],paperSize[2]))
        ptsPick = find_corners(pikachu)
        ptsImg = find_corners(image)
        T = cv2.getPerspectiveTransform(ptsPick, ptsImg)
        pikachu = cv2.warpPerspective(pikachu,T,image.shape[:2])
        image[paperSize[0][1]: paperSize[0][1] + pikachu.shape[0], paperSize[0][0] : paperSize[0][0] + pikachu.shape[1]] = pikachu
        cv2.imshow("Original", imutils.resize(image, height=650))
        cv2.imshow("Scanned", imutils.resize(warped, height=640, width=480))
    cv2.waitKey(0)
