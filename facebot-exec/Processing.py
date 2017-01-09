import Client
import DetectBlackPixels

def phase0DetectAndSendLines(image):
    lines = DetectBlackPixels.findBlackLines(image)
    # highlight = DetectBlackPixels.highlightBlack(image, lines[0], (255, 0, 0))
    # Camera.show_image('highlight', highlight)

    for line in lines:
        if line != []:
            Client.sendLineToServer(line)

def phase1ProcessingFunc(image):
    return
def phase2ProcessingFunc(image):
    return