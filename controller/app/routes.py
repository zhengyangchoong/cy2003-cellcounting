
import base64
import time

try:
	from app.printrun.printcore import printcore
except:
	from printrun.printcore import printcore


import datetime
import subprocess
import os

print(os.getcwd())

class MicroscopeController():

	def __init__(self, port = "/dev/ttyUSB0", offline = False):

		self.offline = offline
		self.port = port

		if not offline:
		
			self.p = printcore(port, 250000)
			self.p.connect()

		self.pos = {'x':0, 'y':0, 'z':0}


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

		command = f"fswebcam -r 2560x1440 --jpeg 90 -D 4 -F 1 --no-banner --save {_filename}"

		process = subprocess.call(command.split(" "))

		time.sleep(4)

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


	def move_rel(self, rel_x = 0, rel_y = 0, rel_z = 0):
		
		target_x = self.pos['x'] + rel_x
		target_y = self.pos['y'] + rel_y
		target_z = self.pos['z'] + rel_z

		self.move(abs_x = target_x, abs_y = target_y, abs_z = target_z)


	def move(self, abs_x = 0, abs_y = 0, abs_z = 0):

		move_str = ""

		if abs_x == "":
			abs_x = 0
		if abs_y == "":
			abs_y = 0
		if abs_z == "":
			abs_z = 0
		
		abs_x = int(abs_x)
		abs_y = int(abs_y)
		abs_z = int(abs_z)

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
			print(move_str)
			if not self.offline:
				self.p.send(f"G0 {move_str}")
		
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
	controller = MicroscopeController('/dev/ttyUSB0')

	return render_template('index.html')


@app.route('/get_image', methods = ['GET', 'POST'])
def get_image():

	fp = controller.acquire()

	print(fp)

	fp = "/".join(fp.split("/")[1:])

	data = {"source": fp}
	data = jsonify(data)

	return data



@app.route('/get_position', methods = ['GET', 'POST'])
def get_position():
	data = {"pos": controller.get_pos()}
	data = jsonify(data)

	return data


@app.route('/move_abs', methods = ['POST', 'GET'])
def move_abs():

	controller.move(request.form['set_x_pos'], request.form['set_y_pos'], request.form['set_z_pos'])
	time.sleep(5)

	print(request.form['set_x_pos'])
	print(request.form['set_y_pos'])
	print(request.form['set_z_pos'])


	data = {"pos": controller.get_pos()}
	data = jsonify(data)

	return render_template('index.html', data = data)

@app.route('/move_home', methods = ['GET', 'POST'])
def move_home():
	controller.home()

	# keep querying

	data = {"pos": controller.get_pos()}
	data = jsonify(data)

	return data


"""
features to implement:

1. motion reporting
2. move to
3. home
4. image display



"""
