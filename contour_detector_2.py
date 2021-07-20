import cv2
import datetime
import numpy as np


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

def contourdetector(image_path, mm_distance = 592, max_area_cells = 1500):
  """
  preprocesses image, performs adaptive Gaussian thresholding and connected components detection to derive cell count by hemocytometer method
  excludes cells on outermost bottom and right grid lines
  :param      image_path:  The image file path to jpg
  :param      mm_distance: number of pixels per mm
  :param      max_area_cells: maximum enclosed area that contour detector will accept for it to count as a cell
  returns an integer as the cell count of the image and gridded image with detected contours
  """
  image = cv2.imread(image_path)
  image = unsharp_mask(image)
  image = cv2.bitwise_not(image) 

  y=200
  x=500

  image = image[y:y+mm_distance, x:x+mm_distance] # use numpy slicing to execute the crop
  kernel = np.ones((2,2),np.uint8)
  sure_bg = cv2.erode(image,kernel,iterations = 1) # apply erosion filter

  drawBottomRightLines(sure_bg)

  gray = cv2.cvtColor(sure_bg, cv2.COLOR_BGR2GRAY) # convert to grayscale for thresholding
  thresh = cv2.adaptiveThreshold(gray,255,cv2.ADAPTIVE_THRESH_GAUSSIAN_C,\
            cv2.THRESH_BINARY,11,2) # adaptive thresholding
  kernel2 = np.ones((2,2),np.uint8)
  thresh = cv2.dilate(thresh,kernel2,iterations = 1) # apply dilation to avoid disconnected contours

  cnts, hierarchy = cv2.findContours(255-thresh, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
  cnts = [cnts[i] for i in range(len(cnts)) if hierarchy[0][i][2] == -1] # count contours with no child contours only

  white_dots = [] 

  for c in cnts:
      area = cv2.contourArea(c)
      if 300 > area > 0:
          cv2.drawContours(image, [c], -1, (255, 255, 12), 2)
          white_dots.append(c)


  drawBasicGrid(image, 148, (52, 52, 52)) # draw vertical and horizontal lines

  output_path = "app/static/capture/{}.jpg".format(datetime.datetime.now(), "%Y%m%d-%H%M%S")

  cv2.imwrite(output_path,image)

  return len(white_dots), output_path # returns cell count and image with drawn contours