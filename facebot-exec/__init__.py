import os
import subprocess
import Client
import SyncGlobals
import Camera
import cv2
import time
from threading import Thread
import Processing

import DetectBlackPixels
import PaperHomography

rectangle_threshold = 20
STATUS_TEXT = [
    "Phase 0: draw lines",
    "Phase 1: play"
]


def gameLoop():
    status = 0

    skip_frames = 20
    while skip_frames > 0:
        Camera.get_image_external()
        skip_frames -= 1

    while True:
        camFrame = Camera.get_image_external()
        camFrame = cv2.flip(camFrame,1)
        camFrame = cv2.resize(camFrame, (640,480))
        SyncGlobals.setCamFrame(camFrame)

        gameFrame = Client.getNextFrameFromServer()

        if gameFrame.any():
            SyncGlobals.setGameFrame(gameFrame)

            pointAsTuple = SyncGlobals.getPointAsTuple()
            paperSizes = SyncGlobals.getPaperSizes()

            if pointAsTuple is not None and paperSizes is not None:
                camFrame = PaperHomography.implantFrameOnPaper(camFrame.copy(), gameFrame, paperSizes, pointAsTuple)

        Camera.show_image("Draw me a way", cv2.flip(camFrame,1), STATUS_TEXT[status])

        # space to continue
        if cv2.waitKey(1) == 32:
            if status == 0:
                scannedInk = SyncGlobals.getScannedInk()

                if scannedInk is not None:
                    # lines = DetectBlackPixels.findBlackLines(cv2.resize(scannedInk, (640,480)))
                    #
                    # for line in lines:
                    #     if line != []:
                    #         Client.sendLineToServer(line)
                    print("hi")
                Client.sendLineToServer([(400,100), (280,450)])
                Client.sendPlayToServer()

            elif status == 1:
                Client.sendResetToServer()

            status = (status + 1) % len(STATUS_TEXT)

        # esc to quit
        if cv2.waitKey(1) == 27:
            Client.sendQuitToServer()
            break


def init():
    # if os.name == 'nt':
    #     unity = subprocess.Popen([os.getcwd() + "\unity_builds\draw_client_windows.exe", "-batchmode"])
    # else:
    #     unity = subprocess.Popen([os.getcwd() + "/unity_builds/draw_client_osx.app/Contents/MacOS/draw_client_osx"])
    #
    # time.sleep(3)

    try:
        Client.start()
        thread = Thread(target=Processing.processingLoop)
        thread.start()
        gameLoop()

    finally:
        Processing.running = False
        cv2.destroyAllWindows()
        Client.stop()
        # unity.terminate()
        print 'bye'

init()
