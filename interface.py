import subprocess
import os
import argparse
from printrun.printcore import printcore
import numpy as np
import cv2
import datetime
import time

import xmlrpc.client



class MicroscopeController():

	def __init__(self):
		self.p = printcore('/dev/ttyUSB0', 250000)

		self.rpc = xmlrpc.client.ServerProxy('http://localhost:7978')

		self.pos = {'x':0, 'y':0, 'z':0}


		# does p.send not return anything? 

	def acquire(self, n = 1):
		"""
		
		
		:param      n:    no. of images to take?
		:type       n:    { type_description }
		"""

		DEFAULT_FOLDER = "raw"
		PROCESSED_FOLDER = "capture"

		for i in range(n):

			file_id = datetime.datetime.strftime(datetime.datetime.now(), "%Y%m%d_%H%M%S")

			command = "fswebcam -r 2560x1440 --jpeg 90 -D 2 -F 1 --no-banner --save raw/{}.jpg".format(file_id)

			process = subprocess.Popen(command.split(" "), stdout = f)

			mtx = np.load("intrinisic_matrix.npy")
			dist = np.load("distortion_coeff.npy")

			img = cv.imread('raw/{}.jpg'.format(file_id))
			h,  w = img.shape[:2]
			newcameramtx, roi = cv2.getOptimalNewCameraMatrix(mtx, dist, (w,h), 1, (w,h))

			dst = cv.undistort(img, mtx, dist, None, newcameramtx)
			# crop the image
			x, y, w, h = roi
			dst = dst[y:y+h, x:x+w]
			cv.imwrite('capture/{}.png'.format(file_id), dst)

	def move(self, abs_x, abs_y):
		self.p.send("G0 X")


	def acquire_and_move(self, n, distance):

		current_position = "0"
		for i in range(n):
			pass
			# self.p.send()
		
	def get_pos(self):
		self.p.send("M114")

	def get_status(self):
		print(self.rpc.status())


if __name__ == "__main__":
	yes = MicroscopeController()

	yes.get_pos()
	yes.get_status()

