# template() as defined uses template.jpg (hardcoded) to template match with 
# a jpg file (preprocessed, file path hardcoded) and shows the bounding boxes

import cv2
import matplotlib.pyplot as plt
import numpy as np

def distance(x1, x2):
	"""
	returns euclidian distance between two tuples
	
	:param      x1:   The x 1
	:type       x1:   (x,y) tuple
	:param      x2:   The x 2
	:type       x2:   (x,y) tuple
	
	:returns:   euclidean distance
	:rtype:     float
	"""
	return np.sqrt((x1[0] - x2[0])**2 + (x1[1] - x2[1])**2)


def bin_coords(position):
	"""
	bins the position output provided by cv2.matchTemplate
	
	:param      position: [x_coords, y_coords] where each are arrays
	:type       position: array
	
	:returns: 	list of (x,y) coordinates which are assumed to be representative
	"""

	binned = []
	bin_radius = 10


	# naive binning, assumes input is alr sorted

	for coord in zip(*position[::-1]):
		new_bin = False

		if len(binned) == 0:
			binned.append(coord)
			continue

		if all([distance(existing_coord, coord) > bin_radius for existing_coord in binned]):
			binned.append(coord)

	return binned


def preprocess(image_path, radius = 750, threshold = 55):
	"""
	performs pre-defined pre-processing steps for microscope photos taken on june 3 by yingyue

	crops and does some filtering. returns a np.array which is the new image

	:param      image_path:  The image file path
	:type       image_path:  a string with the relative / absolute imagepath
	:param      radius: draws a square of 2r * 2r around the centre of the image to crop, default of 750
	:param      threshold: rgb threshold value for low pass filter (since cells are front lit, cell membranes are dark)
	"""

	img = cv2.imread(image_path, 0) #greyscale
	_height, _width = img.shape
	
	img_c = img[_height//2-radius:_height//2+radius, _width//2 - radius: _width//2 + radius]

	img_c = cv2.medianBlur(img_c, 3)

	img_c = ~img_c # invert 

	img_c[img_c < 55] = 0 # removes all the bright stuff in the original image

	return img_c





def template(input_file, template_file):
	"""
	runs template matching

	input_file: file path to input_file, which was manually cropped and preprocessing (testing)
	template_file: file path to template file, has been manually cropped and preprocessed
	"""

	img = cv2.imread(input_file, 0)


	# normalise function--> but not strictly needed + and will have to mess with np types
	#img = img.astype('float64') * 255/np.max(img) 

	template = cv2.imread(template_file, 0)
	
	width, height = template.shape[::-1]

	match = cv2.matchTemplate(img, template, cv2.TM_CCOEFF_NORMED)

	threshold = 0.5 # just lower if needed lol

	position = np.where(match >= threshold)



	binned = bin_coords(position)

	print("Cells detected: ", len(binned))

	for point in binned:
		cv2.rectangle(img, point, (point[0] + width, point[1] + height), 255, 2)

	cv2.imshow('Matched boxes', img)
	cv2.waitKey(0)


if __name__ == "__main__":
	template('cells_4_noise_0.jpg', 'template.jpg')


"""
sliding window experiment which was ditched in favour of template matching

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

template()"""

	# define a 30x30 sliding window, 
