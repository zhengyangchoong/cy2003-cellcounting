import subprocess
import os
import argparse


def capture():

	with open("log.txt", "w") as f:
		command = "fswebcam -r 2560x1440 --jpeg 90 -D 3 -F 1 --no-banner --save capture/test.jpg"

		process = subprocess.Popen(command.split(" "), stdout = f)


capture()



