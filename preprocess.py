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


	#print(data[data > 80])

	

count()

	# define a 30x30 sliding window, 
