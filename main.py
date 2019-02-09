import cv2
import sys
from mail import sendEmail
from flask import Flask, render_template, Response
from camera import VideoCamera
from flask_basicauth import BasicAuth
import time
import threading
import pickle
import logging
from os import listdir

logging.basicConfig(format='%(asctime)s %(levelname)s: %(message)s', level=logging.DEBUG)

email_update_interval = 600 # sends an email only once in this time interval
video_camera = VideoCamera(flip=True) # creates a camera object, flip vertically
object_classifier = cv2.CascadeClassifier("models/facial_recognition_model.xml") # an opencv classifier

files = ["./models/{}".format(f) for f in listdir("./models/") if f.endswith(".xml")]
object_classifiers = [cv2.CascadeClassifier(path) for path in files]
logging.info(files)

# App Globals (do not edit)
app = Flask(__name__)
app.config['BASIC_AUTH_USERNAME'] = 'CHANGE_ME_USERNAME'
app.config['BASIC_AUTH_PASSWORD'] = 'CHANGE_ME_PLEASE'
app.config['BASIC_AUTH_FORCE'] = True

basic_auth = BasicAuth(app)
last_epoch = 0

def check_for_objects():
	global last_epoch
	while True:
		frame, found_obj = video_camera.get_frame_with_objects(object_classifiers)
		# cv2.imwrite( "./thing.jpg", frame )
		if found_obj:

			try:

				t = time.time()

				# make jpg
				# image = video_camera.frame_to_jpeg( frame )
				
				# save image
				logging.debug("saving image")
				# cv2.imwrite("./frames/image/image.{}.jpg".format(t), frame, [int(cv2.IMWRITE_JPEG_QUALITY), 90])
				cv2.imwrite( "./frames/image/image.{}.jpg".format(t), frame )
				# cv2.imwrite( "./thing.jpg", frame )
				# cv2.imshow('img', frame)

				# # save frame
				# logging.debug("saving frame")
				# pickling_on = open("./frames/frame/frame.{}.pickle".format(t),"wb")
				# pickle.dump(frame, pickling_on)
				# pickling_on.close()

				# # save raw
				# logging.debug("saving raw")
				# raw = video_camera.get_raw()
				# pickling_on = open("./frames/raw/raw.{}.pickle".format(t),"wb")
				# pickle.dump(raw, pickling_on)
				# pickling_on.close()

			except Exception as e:
				logging.error("Error saving files", exc_info=True)

		if found_obj and (time.time() - last_epoch) > email_update_interval:
			try:
				last_epoch = time.time()
				logging.info("Sending email")
				# sendEmail(frame.tobytes())
			except Exception as e:
				logging.error("Error sending email", exc_info=True)

@app.route('/')
@basic_auth.required
def index():
    return render_template('index.html')

def gen(camera):
    while True:
        frame = camera.get_jpeg().tobytes()
        yield (b'--frame\r\n'
               b'Content-Type: image/jpeg\r\n\r\n' + frame + b'\r\n\r\n')

@app.route('/video_feed')
def video_feed():
    return Response(gen(video_camera),
                    mimetype='multipart/x-mixed-replace; boundary=frame')

if __name__ == '__main__':
    t = threading.Thread(target=check_for_objects, args=())
    t.daemon = True
    t.start()
    app.run(host='0.0.0.0', debug=False)
