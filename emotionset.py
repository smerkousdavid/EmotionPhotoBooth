import cv2
import glob
import random

import numpy as np
from shutil import copyfile



class Emotions:
    def __init__(self, config):
        #self.emotions = ["neutral", "anger", "contempt", "disgust", "fear", "happy", "sadness", "surprise"]
        self._config = config
        
        self.emotions = []
        
        for emotion, enabled in self._config["emotions"].items():
            if enabled:
                self.emotions.append(emotion)

        print(self.emotions)
        self.faceDet = cv2.CascadeClassifier("%s/haarcascade_frontalface_default.xml" % self._config.cascades)
        self.faceDet2 = cv2.CascadeClassifier("%s/haarcascade_frontalface_alt2.xml" % self._config.cascades)
        self.faceDet3 = cv2.CascadeClassifier("%s/haarcascade_frontalface_alt.xml" % self._config.cascades)
        self.faceDet4 = cv2.CascadeClassifier("%s/haarcascade_frontalface_alt_tree.xml" % self._config.cascades)
        self.fishface = cv2.createFisherFaceRecognizer()
        self.data = {}

    def createDataset(self):
        participants = glob.glob("%s/*" % self._config.source_emotion)

        for x in participants:
            part = "%s" %x[-4:]
            for sessions in glob.glob("%s/*" %x):
                print("Session folder: %s" % sessions)
                for files in glob.glob("%s/*" %sessions):
                    print("Session file: %s" % files)
                    current_session = files[20:-30]
                    file = open(files, 'r')
                    current_line = file.readline()
                    emotion = int(float(current_line))
            
                    sourcefile_emotion = glob.glob("%s/%s/%s/*" % (self._config.source_images, part, current_session))[-1]
                    sourcefile_neutral = glob.glob("%s/%s/%s/*" % (self._config.source_images, part, current_session))[0]
           
                    print(sourcefile_emotion[25:])

                    dest_neut = "unknown"
                    dest_emot = "unknown"

                    try:
                        dest_neut = "%s/neutral/%s" % (self._config.sorted_set, sourcefile_neutral[25:])
                        copyfile(sourcefile_neutral, dest_neut)
                    except:
                        print("Failed copying %s to %s" % (sourcefile_neutral, dest_neut))
                    
                    try:
                        dest_emot = "%s/%s/%s" % (self._config.sorted_set, self.emotions[emotion], sourcefile_emotion[25:])
                        copyfile(sourcefile_emotion, dest_emot)
                    except:
                        print("Failed copying %s to %s" % (sourcefile_emotion, dest_emot))

    def get_emotion_files(self, emotion):
        files = glob.glob("%s/%s/*" % (self._config.dataset, emotion))
        random.shuffle(files)
        training = files[:int(len(files) * 0.8)]
        prediction = files[:-int(len(files) * 0.2)]
        return training, prediction

    def make_sets(self):
        training_data = []
        training_labels = []
        prediction_data = []
        prediction_labels = []
        
        for emotion in self.emotions:
            training, prediction = self.get_emotion_files(emotion)
            for item in training:
                image = cv2.imread(item)
                gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
                training_data.append(gray)
                training_labels.append(self.emotions.index(emotion))
        
            for item in prediction:
                image = cv2.imread(item)
                gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
                prediction_data.append(gray)
                prediction_labels.append(self.emotions.index(emotion))

        return training_data, training_labels, prediction_data, prediction_labels

    def _pre_processing(self, frame):
        gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
        return gray

    def _get_training_images(self, emotion):
        return glob.glob("%s/%s/*" % (self._config.dataset, emotion))
    
    def load_trainer(self):
        self.fishface.load(self._config.trainer_file)

    def train(self):
        print("Training datasets")
        training_data = []
        training_labels = []

        for emotion in self.emotions:
            files = self._get_training_images(emotion)
            for item in files:
                try:
                    raw_frame = cv2.imread(item)
                    try:
                        processed_frame = self._pre_processing(raw_frame)
                    except:
                        print("Failed converting colorspace for image %s" % item)
                        processed_frame = raw_frame
                    training_data.append(processed_frame)
                    training_labels.append(self.emotions.index(emotion))
                except Exception as err:
                    print("Failed to train image %s ERROR: %s" % (item, str(err)))
        print("Found %d images for training\nTraining images for %s..." % (len(training_data),  str(self.emotions)))
        self.fishface.train(training_data, np.asarray(training_labels))
        self.fishface.save(self._config.trainer_file)
        print("Done training!")



    def get(self, frame):
        processed_frame = self._pre_processing(frame)
        toRet = [False, [-1, "none"],  0.0, None]

        try:
            face = self.faceDet.detectMultiScale(processed_frame, scaleFactor=1.1, minNeighbors=10, minSize=(5, 5), flags=cv2.CASCADE_SCALE_IMAGE)
            face2 = self.faceDet2.detectMultiScale(processed_frame, scaleFactor=1.1, minNeighbors=10, minSize=(5, 5), flags=cv2.CASCADE_SCALE_IMAGE)
            face3 = self.faceDet3.detectMultiScale(processed_frame, scaleFactor=1.1, minNeighbors=10, minSize=(5, 5), flags=cv2.CASCADE_SCALE_IMAGE)
            face4 = self.faceDet4.detectMultiScale(processed_frame, scaleFactor=1.1, minNeighbors=10, minSize=(5, 5), flags=cv2.CASCADE_SCALE_IMAGE)
        except:
            print("Failed finding face using the cascades!")
            return toRet

        if len(face) == 1:
            facefeatures = face
        elif len(face2) == 1:
            facefeatures = face2
        elif len(face3) == 1:
            facefeatures = face3
        elif len(face4) == 1:
            facefeatures = face4
        else:
            facefeatures = ""
            print("Current frame is invalid, no face found!")
            return toRet

        for (x, y, w, h) in facefeatures:
            face_cropped = processed_frame[y:y+h, x:x+w]

            try:
                face_resized = cv2.resize(face_cropped, (self._config.image_width, self._config.image_height))
                #cv2.imshow("Face", face_resized)
                prediction, confidence =  self.fishface.predict(face_resized)
                toRet[0] = True
                toRet[1] = [prediction, self.emotions[prediction]]
                toRet[2] = confidence
                toRet[3] = face_resized

                return toRet
            except:
                print("Failed to resize current frame!")

        return toRet


    def run_recognizer_test(self):
        training_data, training_labels, prediction_data, prediction_labels = self.make_sets()
    
        print("training fisher face classifier")
        print("size of training set is: %d images" % len(training_labels))
        self.fishface.train(training_data, np.asarray(training_labels))

        print("predicting classification set")
        cnt = 0
        correct = 0
        incorrect = 0
        for image in prediction_data:
            pred, conf = self.fishface.predict(image)
            if pred == prediction_labels[cnt]:
                correct += 1
                cnt += 1
            else:
                incorrect += 1
                cnt += 1
        return ((100*correct)/(correct + incorrect))

    def run_test(self):
        metascore = []
        for i in range(0, 10):
            print("Running test %d out of 10" % i)
            correct = self.run_recognizer_test()
            print("Got %d percent correct!" % correct)
            metascore.append(correct)
        print("End score meaned %d percent correct!" % np.mean(metascore))

    def __detect_faces(self, emotion):
        files = glob.glob("%s/%s/*" % (self._config.sorted_set, emotion))

        filenum = 0
        for f in files:
            frame = cv2.imread(f)
            try:
                gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
            except:
                print("Failed changing colorspace for image %s" % f)
                gray = frame

            cv2.imshow("Detecting Faces", frame)
            cv2.waitKey(10)
        
            try:
                face = self.faceDet.detectMultiScale(gray, scaleFactor=1.1, minNeighbors=10, minSize=(5, 5), flags=cv2.CASCADE_SCALE_IMAGE)
                face2 = self.faceDet2.detectMultiScale(gray, scaleFactor=1.1, minNeighbors=10, minSize=(5, 5), flags=cv2.CASCADE_SCALE_IMAGE)
                face3 = self.faceDet3.detectMultiScale(gray, scaleFactor=1.1, minNeighbors=10, minSize=(5, 5), flags=cv2.CASCADE_SCALE_IMAGE)
                face4 = self.faceDet4.detectMultiScale(gray, scaleFactor=1.1, minNeighbors=10, minSize=(5, 5), flags=cv2.CASCADE_SCALE_IMAGE)
            except:
                print("Failed finding face using cascade!")
                continue


            if len(face) == 1:
                facefeatures = face
            elif len(face2) == 1:
                facefeatures = face2
            elif len(face3) == 1:
                facefeatures = face3
            elif len(face4) == 1:
                facefeatures = face4
            else:
                facefeatures = ""
                print("Image %s is an invalid image, no face found!" % f)
        

            for (x, y, w, h) in facefeatures:
                print("Found a face in file: %s" % f)
                gray = gray[y:y+h, x:x+w]

                try:
                    out = cv2.resize(gray, (self._config.image_width, self._config.image_height))
                    cv2.imwrite("%s/%s/%d.jpg" % (self._config.dataset, emotion, filenum), out)
                except:
                    print("Image %s Failed to resize/write to file" % f)

            filenum += 1

    def calibrateCascade(self):
        for emotion in self.emotions:
            print("Calibrating for emotion: %s" % emotion)
            self.__detect_faces(emotion)
