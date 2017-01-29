import cv2
import math

BLACK_HIGH_BOUNDRY = 50
ROWS = 640
COLS = 480
SIZE = (ROWS, COLS)
RANGE_Y = range(0, 639)
RANGE_X = range(0, 479)
PAPER_MARGIN = 80

def connectBlack(lines, num, dot, image, pixelBool):
    if pixelBool[dot[0]][dot[1]]:
        return

    pixelBool[dot[0]][dot[1]] = True
    lines[num].append(dot)

    for x in range(dot[0] - 1, dot[0] + 2):
        for y in range(dot[1] - 1, dot[1] + 2):
            if (x in RANGE_X and y in RANGE_Y and
                        image.item(x,y) < 80 and pixelBool[x][y] == False and (x,y) != dot):
                connectBlack(lines, num, (x,y), image, pixelBool)

def connectBlack(result, dot, image, pixelBool):
    if pixelBool[dot[0]][dot[1]]:
        return

    pixelBool[dot[0]][dot[1]] = True
    result.append(dot)

    for x in range(dot[0] - 1, dot[0] + 2):
        for y in range(dot[1] - 1, dot[1] + 2):
            if (x in RANGE_X and y in RANGE_Y and
                        image.item(x,y) < 80 and pixelBool[x][y] == False and (x,y) != dot):
                connectBlack(result, (x,y), image, pixelBool)


def linearDistance(dot1, dot2):
    return math.sqrt(math.pow((dot1[0] - dot2[0]), 2) + math.pow((dot1[1] - dot2[1]), 2))

def findBlackLines(gray_image):
    lines = []
    curLine = []
    bases = []
    pixelBool = [[False] * 640] * 480

    cv2.imshow("scan", gray_image)
    for i in xrange(PAPER_MARGIN, gray_image.shape[0] - PAPER_MARGIN):
        for j in xrange(PAPER_MARGIN, gray_image.shape[1] - PAPER_MARGIN):
            black = (gray_image.item(i, j))

            if (black < BLACK_HIGH_BOUNDRY):
                connectBlack(curLine, (i, j), gray_image, pixelBool)
                if len(curLine) > 50:
                    lines.append(curLine)


    for i in range (len(lines)):
        findLineBase(lines[i], bases, pixelBool)
        if (len(bases) > i):
            lines[i] = sorted(
                    lines[i],
                    lambda dot1, dot2: int(linearDistance(bases[i], dot1) - linearDistance(bases[i], dot2))
                )
    return lines


def highlightBlack(image, dots, color):
    for i in range(len(dots)):
        if (dots[i] != None):
            image.itemset((dots[i][0], dots[i][1], 0), color[0])
            image.itemset((dots[i][0], dots[i][1], 1), color[1])
            image.itemset((dots[i][0], dots[i][1], 2), color[2])
    return image


def isCorner(dot, pixelBool):
    foundOne = False
    for i in range(dot[0] - 1, dot[0] + 2):
        for j in range(dot[1] - 1, dot[1] + 2):
            if (pixelBool[i][j]):
                if (not(foundOne)):
                    foundOne = True
                else:
                    return False
    return True

def findCorner(line, pixelBool):
    for dot in line:
        if isCorner(dot, pixelBool):
            return dot

def findLineBase(line, bases, pixelBool):
    corner = findCorner(line, pixelBool)

    if corner != None:
        bases.append(corner)
