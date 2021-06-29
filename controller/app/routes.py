from app import app
from flask import jsonify, render_template, request
import time
from app.printrun.printcore import printcore

import os

print(os.getcwd())


class MicroscopeController():

	def __init__(self):
		
		self.p = printcore('/dev/ttyUSB1', 250000)
		self.p.connect()

		self.pos = {'x':0, 'y':0, 'z':0}


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
				move_str += f"X{abs_x}"
		if abs_y:
			if 0 <= abs_y <= 150: # hard coded limits
				move_str += f"Y{abs_y}"
		if abs_z:
			if 0 <= abs_z <= 45: # hard coded limits
				move_str += f"Z{abs_z}"

		if not move_str == "":
			print(move_str)
			self.p.send(f"G0 {move_str}")


	def acquire_and_move(self, n, distance):

		current_position = "0"
		for i in range(n):
			pass
			# self.p.send()
		
	def get_pos(self):
		self.p.send("M114")

		position = ""

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


		# return a string

		# update self.pos

	def get_status(self):
		#print(self.rpc.status())

		pass

	def home(self):
		self.p.send("G28")
		time.sleep(5)
		return 0
@app.route('/')
@app.route('/index')
def index():

	global controller
	controller = MicroscopeController()

	return render_template('index.html')


@app.route('/get_position', methods = ['POST'])
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

@app.route('/move_home', methods = ['POST'])
def move_home():
	controller.home()

	# keep querying

	print(controller.get_pos())
	time.sleep(1)
	print(controller.get_pos())
	time.sleep(1)
	print(controller.get_pos())
	time.sleep(1)
	print(controller.get_pos())
	time.sleep(1)

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
