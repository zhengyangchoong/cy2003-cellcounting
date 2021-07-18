
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
 
def thresholdingPreprocessing(img):
    gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY) # convert to grayscale for Otsu's thresholding
    ret, thresh = cv2.threshold(
      gray, 0, 255, cv2.THRESH_BINARY_INV+cv2.THRESH_OTSU) # apply otsu threshold
    kernel = np.ones((1,1),np.uint8)
    thresh = cv2.erode(thresh,kernel,iterations = 1) # apply erosion again to smooth cells so the cell wall is smooth
    return thresh


def contourdetector(image_path, mm_distance = 592, max_area_cells = 1500):
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

  y=200
  x=500

  image = image[y:y+mm_distance, x:x+mm_distance] # use numpy slicing to execute the crop
  kernel = np.ones((2,2),np.uint8)
  sure_bg = cv2.erode(image,kernel,iterations = 1) # apply erosion filter

  ############### Contour Detection for Large Cells ###############
  
  drawBottomRightLines(sure_bg)

  thresh = thresholdingPreprocessing(sure_bg)

  cnts, hierarchy = cv2.findContours(thresh, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
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
  thresh_small = thresholdingPreprocessing(exclude_large_cells)

  cnt_small, hierarchy_small = cv2.findContours(thresh_small, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
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
          cv2.drawContours(image, [c], -1, (36, 255, 12), 2)
          white_dots.append(c)

  drawBasicGrid(image, 148, (52, 52, 52)) # draw vertical and horizontal lines

  output_path = "app/static/capture/{}.jpg".format(datetime.datetime.now(), "%Y%m%d-%H%M%S")

  cv2.imwrite(output_path,image)

  return len(white_dots), output_path # returns cell count and image with drawn contours