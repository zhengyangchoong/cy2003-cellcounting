import subprocess
import os
import argparse


def capture():

	with open("log.txt", "w") as f:
		command = "fswebcam -r 2560x1440 --jpeg 90 -D 4 --no-banner output.jpg"

		process = subprocess.Popen(command.split(" "), stdout = f)


capture()

