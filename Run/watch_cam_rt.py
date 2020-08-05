from vision.ssd.vgg_ssd import create_vgg_ssd, create_vgg_ssd_predictor
from vision.ssd.mobilenetv1_ssd import create_mobilenetv1_ssd, create_mobilenetv1_ssd_predictor
from vision.ssd.mobilenetv1_ssd_lite import create_mobilenetv1_ssd_lite, create_mobilenetv1_ssd_lite_predictor
from vision.ssd.squeezenet_ssd_lite import create_squeezenet_ssd_lite, create_squeezenet_ssd_lite_predictor
from vision.ssd.mobilenet_v2_ssd_lite import create_mobilenetv2_ssd_lite, create_mobilenetv2_ssd_lite_predictor
from vision.utils.misc import Timer
import cv2
import jetson.inference
import jetson.utils
import sys
import argparse
import time
import datetime
from start import found_garbage
import numpy as np

# parse the command line
parser = argparse.ArgumentParser(description='Camera inference')

parser.add_argument("--network", type=str, default="ssd-mobilenet-v2", help="The net type (default: ssd-mobilenet-v2)")
parser.add_argument("--model", type=str, required=True, help="Path to model")
parser.add_argument("--class_labels", type=str, required=True, help="Path to labels txt file")
parser.add_argument("--threshold", type=float, default=0.5, help="minimum detection threshold to use") 

parser.add_argument("--input", default="/dev/video0", help="The input you would like to use")
parser.add_argument("--output", default="display://0", help="The output you would like to use")

parser.add_argument("--no_record", action="store_false", default=False, help="Don't record")
parser.add_argument("--overlay", type=str, default="box,labels,conf", help="detection overlay flags (e.g. --overlay=box,labels,conf)\nvalid combinations are:  'box', 'labels', 'conf', 'none'")

parser.add_argument("--input_blob", help="The name of the input layer you gave when trasforming ONNX")
parser.add_argument("--output_cvg", help="The name of the output layer you gave when trasforming ONNX")
parser.add_argument("--output_bbox", help="The name of the layer related to the coordinates of the bounding boxes")

try:
	args = parser.parse_known_args()[0]
except:
	print("")
	parser.print_help()
	sys.exit(0)

is_headless = ["--headless"] if sys.argv[0].find('console.py') != -1 else [""]

class_names = [name.strip() for name in open(args.class_labels).readlines()]

# load the object detection network
net = jetson.inference.detectNet(args.network, sys.argv, args.threshold)

# create video sources & outputs
input = jetson.utils.videoSource(args.input, argv=sys.argv)
# output = jetson.utils.videoOutput(args.output, argv=sys.argv+is_headless)
output = jetson.utils.videoOutput(args.output, argv=sys.argv)

frameCount = 0
frameWait = 1400 # Wait this many frames before looking for next truck
frameFound = -frameWait

recording = False
startedRecordingFrame = 0

MIN_BG_COUNT = 3000 # Minimum amount of pixels that need to be found in order to start recording
FRAMES_TO_RECORD = frameWait # Will record the next frames until

triggered = False # Allow only one trigger per application

while True:
	frameCount = frameCount + 1
	print('\n\nFrame', frameCount)

	# capture the next image
	image = input.Capture()

	if image:
		# Only will run predictor if Background has changed enough. This saves on resources
		# detect objects in the image (with overlay)
		detections = net.Detect(image, overlay=args.overlay)
		print("detected {:d} objects in image".format(len(detections)))

		for detection in detections:
			print(detection)

		if len(detections):
			Found = True
		else:
			Found = False


		if Found and frameCount > (frameFound + frameWait):
			print(f"Found {len(detections)} objects")
			frameFound = frameCount

			# Only runs truck simulation once per start
			if not triggered:
				print('Found garbage truck')
				found_garbage()
				triggered = True

		# render the image
		output.Render(image)

		# update the title bar
		output.SetStatus("{:s} | Network {:.0f} FPS".format(args.network, net.GetNetworkFPS()))

		# # print out performance info
		# net.PrintProfilerTimes()
		
		# exit on input/output EOS
		if not input.IsStreaming() or not output.IsStreaming():
			break


