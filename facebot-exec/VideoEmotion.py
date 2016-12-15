import cv2
import glob
import random
import numpy as np

# face classifier paths
facePath = "C:\\Users\\dbublil\\Downloads\\opencv\\build\\share\\OpenCV\\haarcascades\\haarcascade_frontalface_default.xml"
smilePath = "C:\\Users\\dbublil\\Downloads\\opencv\\build\\share\\OpenCV\\haarcascades\\haarcascade_smile.xml"
faceCascade = cv2.CascadeClassifier(facePath)

emotions = ["neutral", "anger", "disgust", "happy", "surprise"]  # Emotion list "contempt","fear","sadness",
fishface = cv2.createFisherFaceRecognizer()  # Initialize fisher face classifier

# train face recognizer
def get_files(emotion):# Define function to get file list, randomly shuffle it and split 80/20
    files = glob.glob("dataset/%s/*" % emotion)
    random.shuffle(files)
    training = files[:int(len(files))]  # get first 80% of file list(or not)
    # prediction = files[-int(len(files) * 0.2):]  # get last 20% of file list
    return training

def make_sets():
    training_data = []
    training_labels = []
    for emotion in emotions:
        training = get_files(emotion)
        # Append data to training and prediction list, and generate labels 0-7
        for item in training:
            image = cv2.imread(item)  # open image
            gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)  # convert to grayscale
            training_data.append(gray)  # append image array to training data list
            training_labels.append(emotions.index(emotion))

    return training_data, training_labels

def train_fishface():
    training_data, training_labels = make_sets()

    print "training fisher face classifier"
    print "size of training set is:", len(training_labels), "images"
    fishface.train(training_data, np.asarray(training_labels))
    return

def detect_faces():
    cap = cv2.VideoCapture(0)
    cap.set(3,640)
    cap.set(4,480)

    sF = 1.05

    while True:

        ret, frame = cap.read() # Capture frame-by-frame
        img = frame
        gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
        zoomed_face = []

        faces = faceCascade.detectMultiScale(
            gray,
            scaleFactor= sF,
            minNeighbors=8,
            minSize=(150, 120),
            flags=cv2.cv.CV_HAAR_SCALE_IMAGE
        )
        # ---- Draw a rectangle around the faces
        just_face = 0
        for (x, y, w, h) in faces:
            cv2.rectangle(frame, (x, y), (x+w, y+h), (0, 0, 255), 2)
            roi_gray = gray[y:y+h, x:x+w]
            zoomed_face = frame[y:y+h, x:x+w]
            zoomed_face = cv2.cvtColor(cv2.resize(zoomed_face, (350,350)),cv2.COLOR_BGR2GRAY)
            cv2.imshow('JustFace', zoomed_face)
            print(emotions[fishface.predict(zoomed_face)[0]])


        #cv2.cv.Flip(frame, None, 1)
        cv2.imshow('Face Detector', frame)
        c = cv2.cv.WaitKey(7) % 0x100
        if c == 27: # esc
            break

    cap.release()
    cv2.destroyAllWindows()

#Run the program
train_fishface()
detect_faces()
print "Fin"