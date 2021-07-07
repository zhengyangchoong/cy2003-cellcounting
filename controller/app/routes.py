
import base64
import time

try:
	from app.printrun.printcore import printcore
except:
	from printrun.printcore import printcore


import datetime
import subprocess
import os

import contour_detector


print(os.getcwd())

class MicroscopeController():

	def __init__(self, port = "/dev/ttyUSB0", offline = False):

		self.offline = offline
		self.port = port

		if not offline:
		
			self.p = printcore(port, 250000)
			self.p.connect()

		self.pos = {'x':0, 'y':0, 'z':0}

		self.internal_state = {
			"move_units": "0.1",
			"move_axis": "x",
			"move_direction":"+"
		}

		#warm up camera

		command = f"fswebcam -r 1920x1080 --jpeg 90 -D 4 -F 2 --no-banner"

		process = subprocess.call(command.split(" "))

		time.sleep(4)


	def disconnect(self):
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

		command = f"fswebcam -r 1920x1080 --jpeg 90 -D 4 -F 1 --no-banner --save {_filename}"

		process = subprocess.call(command.split(" "))

		if undistort:

			mtx = np.load("intrinisic_matrix.npy")
			dist = np.load("distortion_coeff.npy")

			img = cv.imread('raw/{}.jpg'.format(file_id))
			h,  w = img.shape[:2]
			newcameramtx, roi = cv2.getOptimalNewCameraMatrix(mtx, dist, (w,h), 1, (w,h))

			dst = cv.undistort(img, mtx, dist, None, newcameramtx)
			# crop the image
			x, y, w, h = roi
			dst = dst[y:y+h, x:x+w]
			_filename = 'capture/{}.png'.format(file_id)
			cv.imwrite(_filename, dst)


		return _filename

	def count_cells(self,fp):
		count, img = contour_detector.contourdetector(fp)

		return (count, img)

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

		target_x = self.pos['x']
		target_y = self.pos['y']
		target_z = self.pos['z']

		if self.internal_state["move_axis"] == "x":
			target_x += distance
		elif self.internal_state["move_axis"] == "y":
			target_y += distance
		elif self.internal_state["move_axis"] == "z":
			target_z += distance

		self.move(abs_x = target_x, abs_y = target_y, abs_z = target_z)


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
					move_str += "X{:.2f}".format(abs_x)
			if abs_y:
				if 0 <= abs_y <= 180: # hard coded limits
					move_str += "Y{:.2f}".format(abs_y)
			if abs_z:
				if 0 <= abs_z <= 45: # hard coded limits
					move_str += "Z{:.2f}".format(abs_z)

			if not move_str == "":
				print("Moving with str G0 ", move_str)
				if not self.offline:
					self.p.send(f"G0 {move_str}")
		except:
			print("failed for some reason")
		
	def get_pos(self):
		position = ""
		if not self.offline:
			self.p.send("M114")

			for i in range(3):
				test_str = self.p.printer.readline()
				print(i, test_str)

				if len(test_str) > 4:
					position = test_str

			position = str(position)

			if position == "":
				return [0,0,0]
			try:

				coords = (position.split(" "))
				coords = [coords[0], coords[1], coords[2]]

				coords = list(map(lambda x: float(x.split(":")[1]), coords))

				print("@@@@", coords)
				return coords
			except:
				return [0,0,0]

		return [0,0,0]

	def get_status(self):
		#print(self.rpc.status())

		pass

	def home(self):

		if not self.offline:
			self.p.send("G28")
			time.sleep(5)
		return 0



from app import app
from flask import jsonify, render_template, request, send_file, make_response
@app.route('/')
@app.route('/index')
def index():

	global controller
	controller = MicroscopeController('/dev/ttyUSB1', offline = False)

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


@app.route('/move_abs', methods = ['POST',])
def move_abs():

	controller.move(request.form['set_x_pos'], request.form['set_y_pos'], request.form['set_z_pos'])
	time.sleep(5)

	print(request.form['set_x_pos'])
	print(request.form['set_y_pos'])
	print(request.form['set_z_pos'])


	data = {"pos": controller.get_pos()}
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
"""
features to implement:

1. motion reporting
2. move to
3. home
4. image display



"""
