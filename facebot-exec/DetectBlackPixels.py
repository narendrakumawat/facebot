import math

BLACK_HIGH_BOUNDRY = 50
ROWS = 640
COLS = 480
SIZE = (ROWS, COLS)
RANGE_Y = range(0, 639)
RANGE_X = range(0, 479)
PAPER_MARGIN = 50

pixelBool = [[False] * 640] * 480

#Recursively attaches all black pixels which form
#a line together to one connected line.
#Also uses memorization to not check the same pixel twice.
def connectBlack(result, dot, image, pixelBools):
    #check if we already visited this pixel.
    if pixelBools[dot[0]][dot[1]]:
        return

    pixelBools[dot[0]][dot[1]] = True
    #add dot to line
    result.append(dot)
    ranger = 8
    #radius of pixels is 8
    for x in range(dot[0] - ranger, dot[0] + ranger):
        for y in range(dot[1] - ranger, dot[1] + ranger):
            if (x in RANGE_X and y in RANGE_Y and
                        image.item(x,y) == 255 and (not pixelBools[x][y]) and (x, y) != dot):
                connectBlack(result, (x,y), image, pixelBools)


def linearDistance(dot1, dot2):
    return math.sqrt(math.pow((dot1[0] - dot2[0]), 2) + math.pow((dot1[1] - dot2[1]), 2))

def findBlackLines(gray_image):
    lines = []
    curLine = [[]] * 1000
    print curLine
    bases = []
    num = 0
    pixelBools = [[False] * 640] * 480
    for i in xrange(PAPER_MARGIN, gray_image.shape[0]):
        for j in xrange(PAPER_MARGIN, gray_image.shape[1]):
            pixel = (gray_image.item(i, j))

            if (pixel  == 255 and not pixelBool[i][j]):
                connectBlack(curLine[num], (i, j), gray_image, pixelBools)
                if len(curLine[num]) > 20:
                    lines.append(curLine[num])
                    num = num + 1
                else:
                    curLine[num] = []


    for i in range (len(lines)):
        findLineBase(lines[i], bases, pixelBool)
        if (len(bases) > i):
            lines[i] = sorted(
                    lines[i],
                    lambda dot1, dot2: int(linearDistance(bases[i], dot1) - linearDistance(bases[i], dot2))
                )
    return lines


#A pixel which is a corner is a pixel
#which has only 1 neighbour, as it is the
#tail of the line.
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
