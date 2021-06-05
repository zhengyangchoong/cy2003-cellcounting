import cv2
import matplotlib.pyplot as plt
import numpy as np

def main():
	img = cv2.imread('IMG_3173.jpg', 0) # 0 is greyscale; there's probably a way to use RGB data to fix the artifacts near the edge but it's not a priority yet

	print(img.shape)

	_height, _width = img.shape

	radius = 750 # it's technically a square

	img_c = img[_height//2-radius:_height//2+radius, _width//2 - radius: _width//2 + radius]

	img_c = cv2.medianBlur(img_c, 3)

	img_c = ~img_c

	img_c[img_c < 55] = 0

	cv2.imwrite("IMG_3173_preproc.jpg", img_c)




	#plt.imshow(img_c)
	#plt.show()

main()

