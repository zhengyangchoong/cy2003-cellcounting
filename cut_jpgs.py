import cv2
import pandas as pd
import numpy as np
from pathlib import Path
import os

# load directory with all the cut jpgs (presumably converted from HEIC)


# assumes its already preprocessed
def cut():

	source_folder = "before_label"
	output_folder = "cut"
	csv_output = "7jun.csv"

	# cut 50x50, downsample to 20x20

	# cut a square, because we're cropping using a square
	# but i'll add padding anyway so it won't matter too much

	# if the img dimension is not an even multiple, add padding

	df = pd.DataFrame(columns = ["filename", "n_cells"])


	for filename in os.listdir(source_folder):
		if filename.endswith(".jpg"):

			c = 0

			img = cv2.imread(os.path.join(source_folder, filename), 0)

			_height, _width = img.shape

			window_size = 50

			done = False

			for i in range(_height//window_size):
				for j in range(_width//window_size):

					if c > 10:
						done = True
						break

					cut_img = img[i*window_size: (i+1)*window_size, j*window_size: (j+1) * window_size]

					_cutname = os.path.join(output_folder, "{}_{:03d}".format(filename, c))

					df.loc[c, "filename"] = _cutname

					cv2.imwrite(_cutname, cut_img)

					c += 1
				if done:
					break

	df.to_csv(csv_output, index = False)



if __name__ == "__main__":
	cut()