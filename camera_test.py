import subprocess
import os
import argparse


def capture():
	command = "fswebcam -r 2560x1440 --jpeg 90 -D 4 --no-banner output.jpg"

	process = subprocess.Popen(command.split(" "), stdout = output)
capture()

