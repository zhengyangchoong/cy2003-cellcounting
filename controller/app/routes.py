
import time

try:
	from app.printrun.printcore import printcore
	
except:
	from printrun.printcore import printcore
	pass

import datetime
import os
import numpy as np
import contour_detector
from pathlib import Path
import cv2
import numpy as np

print(os.getcwd())

class MicroscopeController():

	def __init__(self, offline = False):

		self.offline = offline

		if not offline:
			try:
				ports = [str(p) for p in Path("/dev").glob("ttyUSB*")]
				self.port = ports[0]
			except:
				print("device not connected")

		

		if not offline:
		
			self.p = printcore(ports[0], 250000)
			self.p.connect()

		self.pos = {'x':0, 'y':0, 'z':0}

		self.internal_state = {
			"move_units": "0.1",
			"move_axis": "x",
			"move_direction":"+"
		}

		#warm up camera

		#command = f"fswebcam -r 1920x1080 --jpeg 90 -D 4 -F 2 --no-banner"

		#process = subprocess.call(command.split(" "))


	def disconnect(self):
		self.p.send("M107")
		time.sleep(0.5)
		self.disconnect()
		return 0


	def acquire(self, undistort = False):
		"""
		
		
		:param      n:    no. of images to take?
		:type       n:    { type_description }
		"""

		DEFAULT_FOLDER = "app/static/raw"
		PROCESSED_FOLDER = "app/static/capture"

		if not os.path.exists(DEFAULT_FOLDER):
			os.makedirs(DEFAULT_FOLDER)

		if not os.path.exists(PROCESSED_FOLDER):
			os.makedirs(PROCESSED_FOLDER)


		file_id = datetime.datetime.strftime(datetime.datetime.now(), "%Y%m%d_%H%M%S")

		_filename = os.path.join(DEFAULT_FOLDER, file_id + ".jpg")


		self.cap = cv2.VideoCapture(0)

		if (not self.cap.isOpened()):
			print("Camera not found")

		self.cap.set(cv2.CAP_PROP_FOURCC, cv2.VideoWriter_fourcc('M', 'J', 'P', 'G'))
		width = 1920
		height = 1080
		self.cap.set(cv2.CAP_PROP_FRAME_WIDTH, width)
		self.cap.set(cv2.CAP_PROP_FRAME_HEIGHT, height)


		retval, image = self.cap.read()

		if retval:
			cv2.imwrite(_filename, image)
		else:
			print("camera not available")

		self.cap.release()

		# if undistort:

		# 	mtx = np.load("intrinisic_matrix.npy")
		# 	dist = np.load("distortion_coeff.npy")

		# 	img = cv.imread('raw/{}.jpg'.format(file_id))
		# 	h,  w = img.shape[:2]
		# 	newcameramtx, roi = cv2.getOptimalNewCameraMatrix(mtx, dist, (w,h), 1, (w,h))

		# 	dst = cv.undistort(img, mtx, dist, None, newcameramtx)
		# 	# crop the image
		# 	x, y, w, h = roi
		# 	dst = dst[y:y+h, x:x+w]
		# 	_filename = 'capture/{}.png'.format(file_id)
		# 	cv.imwrite(_filename, dst)


		return _filename

	def count_cells(self,fp):
		count, img = contour_detector.contourdetector(fp)

		return (count, img)

	def simple_move(self, axis = "x", distance = 0):

		target_x = self.pos['x']
		target_y = self.pos['y']
		target_z = self.pos['z']

		if axis == "x":
			target_x += distance
		elif axis == "y":
			target_y += distance
		elif axis == "z":
			target_z += distance

		self.move(abs_x = target_x, abs_y = target_y, abs_z = target_z)

	def move_rel(self, distance):

		if self.internal_state["move_units"] == "0.1":
			distance *= 0.1
		elif self.internal_state["move_units"] == "1.0":
			distance *= 1
		elif self.internal_state["move_units"] == "10":
			distance *= 10

		print("distance to move", distance)

		if self.internal_state["move_direction"] == "-":
			distance *= -1

		self.simple_move(axis = self.internal_state["move_axis"], distance = distance)


	def move(self, abs_x = 0, abs_y = 0, abs_z = 0):

		print(abs_x, abs_y, abs_z)
		try:

			move_str = ""

			if abs_x == "":
				abs_x = 0
			if abs_y == "":
				abs_y = 0
			if abs_z == "":
				abs_z = 0
			
			abs_x = float(abs_x)
			abs_y = float(abs_y)
			abs_z = float(abs_z)

			if abs_x:
				if 0 <= abs_x <= 150: # hard coded limits
					move_str += "X{:.2f} ".format(abs_x)
					self.pos["x"] = abs_x
			if abs_y:
				if 0 <= abs_y <= 180: # hard coded limits
					move_str += "Y{:.2f} ".format(abs_y)
					self.pos["y"] = abs_y
			if abs_z:
				if 0 <= abs_z <= 85: # hard coded limits
					move_str += "Z{:.2f} ".format(abs_z)
					self.pos["z"] = abs_z

			if not move_str == "":
				print("Moving with str G0 ", move_str)
				if not self.offline:
					self.p.send(f"G0 {move_str}")
		except:
			print("Error!")
		
	def get_pos(self):
		position = ""
		if not self.offline:
			self.p.send("M114")

			for i in range(5):
				test_str = self.p.printer.readline()
				print(i, test_str)
				time.sleep(0.20)

				if len(test_str) > 4:
					position = test_str

			position = str(position)

			if position == "":
				return [0,0,0]
			try:

				coords = (position.split(" "))
				coords = [coords[0], coords[1], coords[2]]

				coords = list(map(lambda x: float(x.split(":")[1]), coords))

				self.pos["x"] = coords[0]
				self.pos["y"] = coords[1]
				self.pos["z"] = coords[2]

				print("@@@@", coords)
				return coords
			except:
				return [self.pos["x"], self.pos["y"], self.pos["z"]]



		return [self.pos["x"], self.pos["y"], self.pos["z"]]

	def home(self):

		if not self.offline:
			#self.p.send("M106 S255")
			self.p.send("G28")
			time.sleep(5)

		return 0



from app import app
from flask import json, jsonify, render_template, request, send_file, make_response
@app.route('/')
@app.route('/index')
def index():

	global controller
	controller = MicroscopeController(offline = False)
	controller.home()

	return render_template('index.html')


@app.route('/get_image', methods = ['GET', 'POST'])
def get_image():

	fp = controller.acquire()

	print(fp)

	fp = "/".join(fp.split("/")[1:])

	data = {"source": fp}
	data = jsonify(data)

	return data

@app.route('/capture_and_count', methods = ['GET', 'POST'])
def capture_and_count():

	fp = controller.acquire()

	count, fp = controller.count_cells(fp)

	fp = "/".join(fp.split("/")[1:])

	data = {"source": fp, "count": count}
	data = jsonify(data)

	return data

@app.route('/get_position', methods = ['GET', 'POST'])
def get_position():
	data = {"pos": controller.get_pos()}
	data = jsonify(data)

	return data

def shutdown_server():
    func = request.environ.get('werkzeug.server.shutdown')
    if func is None:
        raise RuntimeError('Not running with the Werkzeug Server')
    func()
    
@app.route('/shutdown', methods=['GET'])
def shutdown():
	shutdown_server()
	controller.cap.release()
	return 'Server shutting down...'

@app.route('/move_abs', methods = ['POST',])
def move_abs():

	controller.move(
		request.values.get("x"),
		request.values.get("y"),
		request.values.get("z"),
	)
	#controller.move(request.form['set_x_pos'], request.form['set_y_pos'], request.form['set_z_pos'])
	time.sleep(5)


	data = {"pos": [controller.pos["x"],controller.pos["y"],controller.pos["z"]]}
	data = jsonify(data)

	return data


@app.route('/move_home', methods = ['GET', 'POST'])
def move_home():
	controller.home()

	# keep querying

	data = {"pos": controller.get_pos()}
	data = jsonify(data)

	return data


@app.route('/set_units', methods = ['POST'])
def set_units():

	controller.internal_state["move_units"] = request.values.get("move_unit")

	#controller.internal_state = state

	data = {"hi": "hi"}
	data = jsonify(data)
	return data

@app.route('/set_axis', methods = ['POST'])
def set_axis():
	controller.internal_state["move_axis"] = request.values.get("move_axis")

	print(controller.internal_state)
	data = {"hi": "hi"}
	data = jsonify(data)
	return data

@app.route('/set_direction', methods = ['POST'])
def set_direction():
	controller.internal_state["move_axis"] = request.values.get("move_direction")

	#print(controller.internal_state)
	data = {"hi": "hi"}
	data = jsonify(data)
	return data


@app.route('/move_by', methods = ['POST'])
def move_by():
	distance = request.values.get('move_by')
	#print("distance returned:",distance)

	controller.move_rel(float(distance))

	time.sleep(1)

	data = {"hi": "hi"}
	data = jsonify(data)
	return data



def getfocus(fp):

	img = cv2.imread(fp, 0)
	
	centre_y = img.shape[0]//2
	centre_x = img.shape[1]//2

	dx = 900
	dy = 900

	img = img[centre_y - dy//2: centre_y + dy//2, centre_x - dx//2: centre_x + dx//2]

	return (cv2.Laplacian(img, cv2.CV_32F).var())


@app.route('/autofocus', methods = ['POST'])
def autofocus():

	#scan_distance = float(request.values.get('scan_distance')) # total distane to travel
	#scan_direction = request.values.get('scan_direction')
	#scan_step = float(request.values.get('scan_step')) # step size
	#
	

	scan_distance = 3
	scan_step = 0.1

	# steps per mm


	# scan direction
	# scan step
	# scan distance
	# input from ^
	# 
	# 
	# 
	# acquire
	# 
	# threshold
	# 
	
	THRESHOLD = 10
	
	values = []


	N_STEP = int(scan_distance // scan_step)
	for i in range(N_STEP):
		controller.simple_move(axis = "z", distance = scan_step)
		fp = controller.acquire()
		time.sleep(0.5)

		_focus = getfocus(fp)
		values.append(_focus)

		print(i, _focus)

		if _focus > THRESHOLD:
			break

	print("distance", i * scan_step, "index", i)

	max_index = values.index(max(values))

	controller.simple_move(axis = "z", distance = -2)

	time.sleep(1)

	controller.simple_move(axis = "z", distance = max_index * scan_step)


	print("max_index", max_index)




	data = {"focal_distance": controller.pos["z"]}
	data = jsonify(data)
	return data


@app.route('/gradient', methods = ['POST'])
def gradient_descent():

	def update_grad(x1, x2, y1, y2):
		try:
			g = (y2-y1)/(x2-x1)	
		except:
			return 0.01
		if g >= 0:
			return np.exp(-np.abs(g))
		else:
			return -1 * np.exp(-np.abs(g))
	
	
	total_scan_range = 3
	
	patience = 5 # wait for 5 steps for any improvement in the focus

	counter = 0 # since last improvement

	initial_scan_step = 0.2

	max_iterations = 20
	total_steps = 0

	starting = True

	X = []
	Y = []

	best_score = 0

	start_z = controller.pos["z"]

	while counter < patience:

		if controller.pos["z"] - start_z >= total_scan_range or total_steps >= max_iterations:
			print("Could not find maximum focus within specified range of {}mm".format(total_scan_range))

			# print report / return json with report on max location, then move to that location
			break
		if starting:
			X.append(start_z)
			Y.append(getfocus(controller.acquire()))

			controller.simple_move(axis = "z", distance = initial_scan_step)

			X.append(initial_scan_step)
			Y.append(getfocus(controller.acquire()))

			best_score = max(Y)

			

			starting = False

		else:
			dx = update_grad(X[-2], X[-1], Y[-2], Y[-1])	
			print(X,Y)
			print("DELTA X: ", dx)		
			controller.simple_move(axis = "z", distance = dx)
			X.append((X[-1] + dx))
			Y.append(getfocus(controller.acquire()))

		print("position: ", X[-1], "best score: ", max(Y), "best score position", X[Y.index(max(Y))])
		if Y[-1] >= best_score:
			best_score = max(Y)
			counter = 0

		total_steps += 1

	# best location and index:

	best_focus = max(Y)
	best_location = X[Y.index(max(Y))]	
	controller.move(abs_z = best_location, abs_x = "", abs_y = "")

	data = {"Y": str(best_focus), "X": str(best_location)}
	print(data)
	data = jsonify(data)

	return data

	


		






