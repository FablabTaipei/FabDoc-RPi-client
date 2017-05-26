from picamera import PiCamera
from picamera.array import PiRGBArray
from PIL import Image
import cv2
import zbarlight
import numpy

from pydispatch import dispatcher
import time
import threading

class Camera:
	def __init__(self, resolution=(640, 480), framerate=30, timeGap=10, path='./'):
		self.camera = PiCamera()
		self.camera.resolution = resolution
		self.camera.framerate = framerate
		self.timeGap = timeGap
		self.path = path
		self.isDecoded = False
		self.code = ""

	def decodeImage(self, image):
		""" Check an image for a QR code, return as string """
		image_string = image.tostring()
		try:
			code = zbarlight.qr_code_scanner(image_string, self.camera.resolution[0], self.camera.resolution[1])
			return code
		except:
			return

	def scanQRcode(self):
		rawCapture = PiRGBArray(self.camera, size = self.camera.resolution)
		# stream = io.BytesIO()
		for frame in self.camera.capture_continuous(rawCapture,
							   format = "bgr",
							   use_video_port = True):
			# grab image as numpy array
			image = frame.array

			# convert image to grayscale and decode
			gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
			decoded = self.decodeImage(gray)
			# rawCapture.truncate(0)
			rawCapture.truncate(0)

			if decoded:
				self.isDecoded = True
				self.code = decoded
				break

	def captureTimeLapse(self):
		for filename in self.camera.capture_continuous(self.path):
			print('Captured %s' % filename)
			time.sleep(self.timeGap)

	def run(self):
		qrThread = threading.Thread(target=self.scanQRcode)
		qrThread.start()
		print "Start capture QR code"
		qrThread.join()

		captureThread = threading.Thread(target=self.captureTimeLapse)
		captureThread.start()

