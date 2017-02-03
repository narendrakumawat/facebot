import socket
import sys
import cv2
import numpy as np
import base64
from PIL import Image
from StringIO import StringIO

# Create a TCP/IP socket
sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

# Convert compressed PNG string to OpenCV format
def readb64(base64_string):
    sbuf = StringIO()
    sbuf.write(base64.b64decode(base64_string))
    pimg = Image.open(sbuf)
    return cv2.cvtColor(np.array(pimg), cv2.COLOR_RGB2BGR)

# Connect the socket to the port where the server is listening
def start():
    server_address = ('localhost', 1337)
    print >>sys.stderr, 'connecting to %s port %s' % server_address
    sock.connect(server_address)

# Close the socket
def stop():
    print >> sys.stderr, 'closing socket'
    sock.close()

# Send single line to server
def sendLineToServer(line):
    try:
        message = str(line) + '<EOL>'
        sock.sendall(message)

    except Exception, e:
        print >> sys.stderr, e

# Send request for next frame to server, and cache the recieved data
def getNextFrameFromServer():
    try:
        message = '<NEXT>'
        sock.sendall(message)

        # Wait for the complete response
        img_str = ''
        while not img_str.endswith('<EOF>'):
            data_str = sock.recv(16384)
            img_str += data_str

        # when frame received
        if len(img_str) > 0:
            frame = readb64(img_str.replace('<EOF>', ''))

        return frame

    except Exception, e:
        print >> sys.stderr, e

# Send play request to server
def sendPlayToServer():
    try:
        message = '<PLAY>'
        sock.sendall(message)

    except Exception, e:
        print >> sys.stderr, e

# Send reset game request to server
def sendResetToServer():
    try:
        message = '<RESET>'
        sock.sendall(message)

    except Exception, e:
        print >> sys.stderr, e

# Send shutdown request to server
def sendQuitToServer():
    try:
        message = '<QUIT>'
        sock.sendall(message)

    except Exception, e:
        print >> sys.stderr, e
