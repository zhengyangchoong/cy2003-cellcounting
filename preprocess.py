import cv2
import matplotlib.pyplot as plt
import numpy as np
from scipy import signal

def main():
	img = cv2.imread('IMG_3173.jpg', 0) # 0 is greyscale; there's probably a way to use RGB data to fix the artifacts near the edge but it's not a priority yet

	print(img.shape)

	_height, _width = img.shape

	radius = 750 # it's technically a square

	img_c = img[_height//2-radius:_height//2+radius, _width//2 - radius: _width//2 + radius]

	img_c = cv2.medianBlur(img_c, 3)

	img_c = ~img_c

	img_c[img_c < 55] = 0 # threshold derived by looking a a histogram

	cv2.imwrite("IMG_3173_preproc.jpg", img_c)

	#plt.imshow(img_c)
	#plt.show()

#main()

def distance(x1, x2):
	# x1 and x2 are each tuples

	return np.sqrt((x1[0] - x2[0])**2 + (x1[1] - x2[1])**2)


def bin_coords(position):

	binned = []
	bin_radius = 10


	# naive binning, assumes input is alr sorted

	for coord in zip(*position[::-1]):
		#print(coord)
		new_bin = False

		if len(binned) == 0:
			binned.append(coord)
			continue

		if all([distance(existing_coord, coord) > bin_radius for existing_coord in binned]):
			binned.append(coord)

	return binned



def template():

	img = cv2.imread('cells_4_noise_0.jpg', 0)
	#img = img.astype('float64') * 255/np.max(img)

	template = cv2.imread('template.jpg', 0)
	#template = template.astype('float64') * 255/np.max(template)
	width, height = template.shape[::-1]

	match = cv2.matchTemplate(img, template, cv2.TM_CCOEFF_NORMED)

	threshold = 0.5 # just lower if needed lol

	position = np.where(match >= threshold)

	print(position)

	binned = bin_coords(position)

	for point in binned:
		cv2.rectangle(img, point, (point[0] + width, point[1] + height), 255, 2)


	# for point in zip(*position[::-1]): #draw the rectangle around the matched template
 	#	
	cv2.imshow('Template Found', img)
	cv2.waitKey(0)


def count():

	img = cv2.imread('cells_4_noise_0.jpg', 0)

	img = img.astype('float64') * 255/np.max(img)
	

	heatmap = np.zeros((img.shape[0], img.shape[1]))

	print(img.shape)

	win_size = 30 # 30x30 square
	step_size = 15

	data = []

	for c, i in enumerate(range(0, img.shape[0] - win_size + 1, step_size)):
		for d, j in enumerate(range(0, img.shape[1] - win_size + 1, step_size)):
			data.append(np.sum(img[i:i+win_size, j:j+win_size]))

	data = np.array(data)
	data = data/(win_size**2)

	plt.hist(data)
	plt.show()

	data = data.reshape((c + 1,d + 1))

	plt.imshow(data)
	plt.show()

template()

	# define a 30x30 sliding window, 
