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

STATUS_TEXT = [
    "Phase 0: draw lines (SPACE to play, ESC to quit)",
    "Phase 1: play (SPACE to reset, ESC to quit)"
]


def gameLoop():
    status = 0

    # skip first 20 frames of video capture to allow camera initialization
    skip_frames = 20
    while skip_frames > 0:
        Camera.get_image_external()
        skip_frames -= 1

    while True:
        # get and cache current camera frame
        camFrame = Camera.get_image_external()
        camFrame = cv2.flip(camFrame,1)
        camFrame = cv2.resize(camFrame, (640,480))
        SyncGlobals.setCamFrame(camFrame)

        # get next game frame from server
        gameFrame = Client.getNextFrameFromServer()

        if gameFrame.any():
            # cache current game frame
            SyncGlobals.setGameFrame(gameFrame)

            # get cached paper position and size
            pointAsTuple = SyncGlobals.getPointAsTuple()
            paperSizes = SyncGlobals.getPaperSizes()

            # paper position recognized
            if pointAsTuple is not None and paperSizes is not None:
                # merge game frame into camera frame on top of recognized paper
                camFrame = PaperHomography.implantFrameOnPaper(camFrame.copy(), gameFrame, paperSizes, pointAsTuple)

        Camera.show_image("Draw me a way", cv2.flip(camFrame,1), STATUS_TEXT[status])

        # space to continue
        if cv2.waitKey(1) == 32:
            # user wants to start playing the game
            if status == 0:
                # get cached state of paper
                scannedInk = SyncGlobals.getScannedInk()

                if scannedInk is not None:
                    # capture lines from cached state of paper
                    edgy = cv2.resize(scannedInk,(640,480))
                    lines = DetectBlackPixels.findBlackLines(cv2.Canny(edgy, 100, 300))

                    # send recognized lines to game server, but limit to 4 lines
                    num = 0
                    for line in lines:
                        if line is not []:
                            num += 1
                            if num < 4:
                                Client.sendLineToServer(line)
                            else:
                                break

                # start playing the game
                Client.sendPlayToServer()

            # user wants to reset the game
            elif status == 1:
                Client.sendResetToServer()

            # advance game state
            status = (status + 1) % len(STATUS_TEXT)

        # user wants to quit
        if cv2.waitKey(1) == 27:
            Client.sendQuitToServer()
            break


def init():
    # start unity game process for current os
    if os.name == 'nt':
        unity = subprocess.Popen([os.getcwd() + "\unity_builds\draw_client_windows.exe"])
    else:
        unity = subprocess.Popen([os.getcwd() + "/unity_builds/draw_client_osx.app/Contents/MacOS/draw_client_osx"])

    # wait for unity process to load
    time.sleep(7)

    try:
        # start communication with game server
        Client.start()
        thread = Thread(target=Processing.processingLoop)
        thread.start()
        # start game processing loop
        gameLoop()

    finally:
        # shut down connection, close windows, and terminate
        Processing.running = False
        cv2.destroyAllWindows()
        Client.stop()
        unity.terminate()
        print 'bye'

init()
