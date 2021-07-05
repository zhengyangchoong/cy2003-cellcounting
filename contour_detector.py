import cv2
import numpy as np


def contourdetector(image_path, mm_distance = 592, max_area_cells = 1500):
  """
  preprocesses image, performs Otsu's thresholding and connected components detection to derive cell count by hemocytometer method
  excludes cells on outermost bottom and right grid lines

  :param      image_path:  The image file path to jpg
  :param      mm_distance: number of pixels per mm
  :param      max_area_cells: maximum enclosed area that contour detector will accept for it to count as a cell

  returns an integer as the cell count of the image
  """
  image = cv2.imread(image_path)
  image = cv2.bitwise_not(image) 
  height, width, channels = image.shape

  y=200
  x=500

  image = image[y:y+mm_distance, x:x+mm_distance] # use numpy slicing to execute the crop
  kernel = np.ones((2,2),np.uint8)
  sure_bg = cv2.erode(image,kernel,iterations = 1) # apply erosion filter

  sure_bg = cv2.copyMakeBorder(sure_bg, 0, 5, 0, 5, cv2.BORDER_CONSTANT, value=(52, 52, 52)) # add bottom and right outermost gridline to ignore cells on these lines

  gray = cv2.cvtColor(sure_bg, cv2.COLOR_BGR2GRAY) # convert to grayscale for Otsu's thresholding
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

  return len(white_dots) # cell count

