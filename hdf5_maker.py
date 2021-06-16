import h5py
import pandas as pd
import cv2
import numpy as np
import os
from pathlib import Path


def make_hdf5():

	df = pd.read_csv('training_data/3n4_50x50.csv') 

	output_hdf5 = "training_data/3n4.hdf5"

	all_files = ([str(p) for p in Path("training_data/3_50x50").glob("*.png")])

	hf = h5py.File(output_hdf5, 'w')

	for filename in all_files:
		_filename = (filename.split("/")[-1])

		if df.loc[df['filename'] == _filename, 'n_cells'].iloc[0] > 2:
			continue

		_img = cv2.imread(filename, 0) # greyscale model

		_img = cv2.resize(_img, dsize=(40, 40), interpolation=cv2.INTER_CUBIC)
		#_img = cv2.normalize(_img, None, alpha=0, beta=1, norm_type=cv2.NORM_MINMAX, dtype=cv2.CV_32F)
		_img = _img.astype("float32") / 255.0
		_img = _img.reshape(_img.shape + (1,))

		_g = hf.create_dataset(_filename, (40,40, 1), data = _img)

	# read csvs

	hf.close()

make_hdf5()

# df.loc[df['filename'] == '3cut0_0.png', 'n_cells'].iloc[0]