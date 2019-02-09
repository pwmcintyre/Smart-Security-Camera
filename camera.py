import cv2
from imutils.video.pivideostream import PiVideoStream
import imutils
import time
import numpy as np
from picamera.array import PiRGBArray
from picamera import PiCamera
from fractions import Fraction
import logging

class VideoCamera(object):

    def __init__(self, flip = False):

        self.vs = PiVideoStream(resolution=(640, 480), framerate=6).start()
        self.flip = flip

        # # https://picamera.readthedocs.io/en/release-1.13/api_camera.html
        # self.camera = PiCamera(
        #     resolution=(640, 480),
        #     framerate=Fraction(5, 1),
        #     # rotation=90,
        #     sensor_mode=3,
        # )
        # self.rawCapture = PiRGBArray(self.camera, size=(640, 480))

		# self.stream = self.camera.capture_continuous(
        #     self.rawCapture,
		# 	format="bgr",
        #     use_video_port=True,
        # )

        time.sleep(1.0)

    def __del__(self):
        self.vs.stop()

    def flip_if_needed(self, frame):
        if self.flip:
            return np.flip(frame, 0)
        return frame

    def get_frame(self):
        frame = self.vs.read()
        # frame = self.camera.array
        frame = self.flip_if_needed(self.vs.read())
        # return frame.copy()
        return frame

    def get_jpeg(self):
        frame = self.get_frame()
        jpeg = self.frame_to_jpeg(frame)
        return jpeg

    def frame_to_jpeg(self, frame):
        ret, jpeg = cv2.imencode('.jpg', frame)
        return jpeg

    def get_frame_with_objects(self, classifiers):
        found_objects = False
        frame = self.get_frame().copy()
        gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)

        for classifier in classifiers:

            objects = classifier.detectMultiScale(
                gray,
                scaleFactor=1.1,
                minNeighbors=5,
                minSize=(30, 30),
                flags=cv2.CASCADE_SCALE_IMAGE
            )

            if len(objects) > 0:
                found_objects = True

            # Draw a rectangle around the objects
            for (x, y, w, h) in objects:
                cv2.rectangle(frame, (x, y), (x + w, y + h), (0, 255, 0), 2)

        return (frame, found_objects)


