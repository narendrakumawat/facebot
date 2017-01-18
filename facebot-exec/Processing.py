import Client
import DetectBlackPixels
import PaperHomography

def phase0DetectAndSendLines(image):
    paperPoints = PaperHomography.getPaperPoints(image)
    scannedContent = PaperHomography.scanInkFromImage(image,paperPoints)
    lines = DetectBlackPixels.findBlackLines(scannedContent)
    # highlight = DetectBlackPixels.highlightBlack(image, lines[0], (255, 0, 0))
    # Camera.show_image('highlight', highlight)

    for line in lines:
        if line != []:
            Client.sendLineToServer(line)

def phase1ProcessingFunc(image):
    return
def phase2ProcessingFunc(image):
    return