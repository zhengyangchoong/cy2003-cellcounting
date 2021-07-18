import cv2
import numpy as np
import matplotlib.pyplot as plt


def contourdetector(image_path, output_path, mm_distance = 592, max_area_cells = 1500, debug = False, image_data = None, static = 0):
	"""
	preprocesses image, performs Otsu's thresholding and connected components detection to derive cell count by hemocytometer method
	excludes cells on outermost bottom and right grid lines

	:param      image_path:  The image file path to jpg
	:param      mm_distance: number of pixels per mm
	:param      max_area_cells: maximum enclosed area that contour detector will accept for it to count as a cell

	returns an integer as the cell count of the image and gridded image with detected contours
	"""
	if image_path == "":
		image = image_data
	else:
		image = cv2.imread(image_path)
	#image = cv2.bitwise_not(image) 
	try:
		height, width, channels = image.shape
	except:
		height, width = image.shape
	original = image.copy()

	y=int(height//2 - mm_distance//2)
	x=int(width//2 - mm_distance//2)

	image = image[y:y+mm_distance, x:x+mm_distance] # use numpy slicing to execute the crop
	kernel = np.ones((2,2),np.uint8)
	sure_bg = cv2.erode(image,kernel,iterations = 1) # apply erosion filter

	sure_bg = cv2.copyMakeBorder(sure_bg, 0, 5, 0, 5, cv2.BORDER_CONSTANT, value=(52, 52, 52)) # add bottom and right outermost gridline to ignore cells on these lines

	gray = cv2.cvtColor(sure_bg, cv2.COLOR_BGR2GRAY) # convert to grayscale for Otsu's thresholding

	if not static:
		ret, thresh = cv2.threshold(
			gray, static, 255, cv2.THRESH_BINARY_INV) # apply otsu threshold
	else:
		ret, thresh = cv2.threshold(
			gray, 0, 255, cv2.THRESH_BINARY_INV+cv2.THRESH_OTSU) # apply otsu threshold
	kernel2 = np.ones((1,1),np.uint8)
	thresh = cv2.erode(thresh,kernel,iterations = 1) # apply erosion again to smooth cells so the cell wall is smooth


	cnts, hierarchy = cv2.findContours(thresh, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
	cnts = [cnts[i] for i in range(len(cnts)) if hierarchy[0][i][2] == -1] # count contours with no child contours only

	white_dots = [] # used contours as blob detection is more suited for detecting black or grey blobs

	for c in cnts:
		area = cv2.contourArea(c)
		if max_area_cells > area :
			cv2.drawContours(image, [c], -1, (36, 255, 12), 2)
			white_dots.append(c)

	drawBasicGrid(image, 148, (52, 52, 52)) # draw vertical and horizontal lines
	image = cv2.copyMakeBorder(image, 7, 5, 7, 5, cv2.BORDER_CONSTANT, value=(52, 52, 52)) # draw border lines

	if debug:
		f, axarr = plt.subplots(nrows=1,ncols=4)
		plt.sca(axarr[0]); 
		plt.imshow(original); plt.title('Original')
		plt.sca(axarr[1]); 
		plt.imshow(sure_bg); plt.title('Image Sharpen and Erosion')
		plt.sca(axarr[2]); 
		plt.imshow(thresh); plt.title('Otsu\'s Thresholding')
		plt.sca(axarr[3]); 
		plt.imshow(image); plt.title(f'Detected Contours with Cell Count:{len(white_dots)}')
		#plt.savefig('/content/gdrive/MyDrive/CY2003_MnT/blobs_n_contours/preprocessed_contours_without_sharpening_webcam.png',bbox_inches = 'tight')
		fig = plt.gcf()       
		fig.set_size_inches(8,6)
		plt.show()
	#output_path = "app/static/capture/{}.jpg".format(datetime.datetime.now(), "%Y%m%d-%H%M%S")
	if output_path == "":
		return len(white_dots), image
	else:
		cv2.imwrite(output_path, image)
	return len(white_dots), output_path # returns cell count and image with drawn contours



#git version


def drawBasicGrid(img, pxstep, colour):
	"""
	adds horizontal and vertical lines on image input to mimic hemocytometer gridlines
	:param      img: 3d matrix of image
	:param      pxstep: pixel distance between gridlines
	:param      colour: colour of lines in RGB
	"""
	x = pxstep 
	y = pxstep 
	#Draw all x lines
	while x < img.shape[1]:
		cv2.line(img, (x, 0), (x, img.shape[0]), color=colour, thickness=5)
		x += pxstep 
	
	# Draw all y lines
	while y < img.shape[0]:
		cv2.line(img, (0, y), (img.shape[1], y), color=colour,thickness=5)
		y += pxstep 
	cv2.line(img, (0,img.shape[0]), (img.shape[1],img.shape[0]), color = colour, thickness = 5) # bottom 
	cv2.line(img, (img.shape[1],img.shape[0]), (img.shape[1],0), color = colour, thickness = 5) # right
	cv2.line(img, (0,img.shape[0]), (0,0), color = colour, thickness = 5) # left
	cv2.line(img, (0,0), (img.shape[1],0), color = colour, thickness = 5) # top

def drawBottomRightLines(img):
	# add bottom and right outermost gridline to ignore cells on these lines
	cv2.line(img, (0,img.shape[0]), (img.shape[1],img.shape[0]), color = (52,52,52), thickness = 5) 
	cv2.line(img, (img.shape[1],img.shape[0]), (img.shape[1],0), color = (52,52,52), thickness = 5)
 
def thresholdingPreprocessing(img, otsu = True, static = 0):
	gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY) # convert to grayscale for Otsu's thresholding
	if otsu:
		ret, thresh = cv2.threshold(gray, 0, 255, cv2.THRESH_BINARY_INV+cv2.THRESH_OTSU) # apply otsu threshold
	else:
		ret, thresh = cv2.threshold(gray, static, 255, cv2.THRESH_BINARY_INV)
	
	kernel = np.ones((1,1),np.uint8)
	thresh = cv2.erode(thresh,kernel,iterations = 1) # apply erosion again to smooth cells so the cell wall is smooth
	return thresh

def lookup_curve(img, i = 0):

	kernel = np.array([[-1,-1,-1], [-1,9,-1], [-1,-1,-1]])
	img = cv2.filter2D(img, -1, kernel)
	#img = unsharp_mask(img)
	thresh = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)

	lut_in = np.array([0, 93, 126, 255])
	lut_out = np.array([255, 73, 0, 0])

	lut_8u = np.interp(np.arange(0,256), lut_in, lut_out).astype(np.uint8)

	#print(lut_8u)

	thresh = cv2.LUT(thresh, lut_8u)
	if i == 0:
		ret, thresh = cv2.threshold(thresh, 0, 255, cv2.THRESH_BINARY_INV + cv2.THRESH_OTSU)
	else:
		ret, thresh = cv2.threshold(thresh, i, 255, cv2.THRESH_BINARY_INV)
	kernel = np.ones((1,1),np.uint8)
	thresh = cv2.erode(thresh, kernel,iterations = 1) # apply erosion again to smooth cells so the cell wall is smooth

	thresh = cv2.bitwise_not(thresh)
	return thresh

def unsharp_mask(image, kernel_size=(3, 3), sigma=1.0, amount=0.5, threshold=0):
	"""Return a sharpened version of the image, using an unsharp mask."""
	blurred = cv2.GaussianBlur(image, kernel_size, sigma)
	sharpened = float(amount + 1) * image - float(amount) * blurred
	sharpened = np.maximum(sharpened, np.zeros(sharpened.shape))
	sharpened = np.minimum(sharpened, 255 * np.ones(sharpened.shape))
	sharpened = sharpened.round().astype(np.uint8)
	if threshold > 0:
		low_contrast_mask = np.absolute(image - blurred) < threshold
		np.copyto(sharpened, image, where=low_contrast_mask)
	return sharpened

def test_1(image_path, mm_distance = 592, max_area_cells = 1500, debug = False, static = 0):
	"""
	preprocesses image, performs Otsu's thresholding and connected components detection to derive cell count by hemocytometer method
	excludes cells on outermost bottom and right grid lines
	:param      image_path:  The image file path to jpg
	:param      mm_distance: number of pixels per mm
	:param      max_area_cells: maximum enclosed area that contour detector will accept for it to count as a cell
	returns an integer as the cell count of the image and gridded image with detected contours
	"""
	image = cv2.imread(image_path)
	image = cv2.bitwise_not(image) 
	original = image.copy()
	h, w, _ = image.shape

	y=int(image.shape[0]/2 - mm_distance/2)
	x=int(image.shape[1]/2 - mm_distance/2)

	image = image[y:y+mm_distance, x:x+mm_distance] # use numpy slicing to execute the crop
	kernel = np.ones((2,2),np.uint8)
	sure_bg = cv2.erode(image,kernel,iterations = 1) # apply erosion filter

	

	############### Contour Detection for Large Cells ###############

	drawBottomRightLines(sure_bg)

	#thresh = thresholdingPreprocessing(sure_bg, otsu = False, static = 55)
	thresh = lookup_curve(sure_bg, static)	

	cnts, hierarchy = cv2.findContours(thresh, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
	#print(cnts)
	cnts = [cnts[i] for i in range(len(cnts)) if hierarchy[0][i][2] == -1] # count contours with no child contours only

	############### Contour Detection for Small Cells ###############

	# exclude large cells
	exclude_large_cells = image.copy()
	for c in cnts:
		area = cv2.contourArea(c)
		if 1500 > area > 90:
			cv2.drawContours(exclude_large_cells, [c], -1, (110, 110, 110), cv2.FILLED) # isolate small cells by removing large cells
			cv2.drawContours(exclude_large_cells, [c], -1, (110,110,110), 6) # draw border

	# contour detection
	#thresh_small = thresholdingPreprocessing(exclude_large_cells)
	thresh_small = lookup_curve(exclude_large_cells, static)

	cnt_small, hierarchy_small = cv2.findContours(thresh_small, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
	#print(cnt_small)
	cnt_small = [cnt_small[i] for i in range(len(cnt_small)) if hierarchy_small[0][i][2] == -1] 

	############### Contour Drawing for All Cells #######################
	white_dots = [] # used contours as blob detection is more suited for detecting black or grey blobs

	for c in cnt_small: 
		area = cv2.contourArea(c)
		if 90 > area > 0:
			cv2.drawContours(image, [c], -1, (36, 255, 12), 2)
			white_dots.append(c)

	for c in cnts:
		area = cv2.contourArea(c)
		if max_area_cells > area > 90 :
			cv2.drawContours(image, [c], -1, (200, 255, 12), 2)
			white_dots.append(c)

	drawBasicGrid(image, 148, (52, 52, 52)) # draw vertical and horizontal lines

	#output_path = "app/static/capture/{}.jpg".format(datetime.datetime.now(), "%Y%m%d-%H%M%S")

	if debug:
		f, axarr = plt.subplots(nrows=2,ncols=2)
		plt.sca(axarr[0, 0]); 
		plt.imshow(original, cmap = "binary"); plt.title('Original')
		plt.sca(axarr[0, 1]); 
		plt.imshow(sure_bg, cmap = "binary"); plt.title('Image Sharpen and Erosion')
		plt.sca(axarr[1 ,0]); 
		plt.imshow(thresh, cmap = "binary"); plt.title('Thresholding')
		plt.sca(axarr[1, 1]); 
		plt.imshow(image, cmap = "binary"); plt.title(f'Detected Contours with Cell Count:{len(white_dots)}')
		#plt.savefig('/content/gdrive/MyDrive/CY2003_MnT/blobs_n_contours/preprocessed_contours_without_sharpening_webcam.png',bbox_inches = 'tight')
		fig = plt.gcf()       
		fig.set_size_inches(8,6)
		fig.set_dpi(150)
		plt.show()

	return len(white_dots), image # returns cell count and image with drawn contours