from vision.ssd.vgg_ssd import create_vgg_ssd, create_vgg_ssd_predictor
from vision.ssd.mobilenetv1_ssd import create_mobilenetv1_ssd, create_mobilenetv1_ssd_predictor
from vision.ssd.mobilenetv1_ssd_lite import create_mobilenetv1_ssd_lite, create_mobilenetv1_ssd_lite_predictor
from vision.ssd.squeezenet_ssd_lite import create_squeezenet_ssd_lite, create_squeezenet_ssd_lite_predictor
from vision.ssd.mobilenet_v2_ssd_lite import create_mobilenetv2_ssd_lite, create_mobilenetv2_ssd_lite_predictor
from vision.utils.misc import Timer
import cv2
import sys
import argparse
import time
import datetime
from start import found_garbage
import numpy as np

# parse the command line
parser = argparse.ArgumentParser(description='Camera inference')

parser.add_argument("--net_type", type=str, default="mb1-ssd", help="The net type (default: mb1-ssd)")
parser.add_argument("--model_path", type=str, required=True, help="Path to model")
parser.add_argument("--label_path", type=str, required=True, help="Path to labels txt file")

parser.add_argument("--input", default="0", help="The input you would like to use")

parser.add_argument("--show", action="store_true", default=False, help="Whether to show what's going on or not")
parser.add_argument("--manual", action="store_true", default=False, help="Whether to manually go frame by frame")
parser.add_argument("--no_record", action="store_false", default=False, help="Don't record")

args = parser.parse_args()

class_names = [name.strip() for name in open(args.label_path).readlines()]

if args.net_type == 'vgg16-ssd':
    net = create_vgg_ssd(len(class_names), is_test=True)
elif args.net_type == 'mb1-ssd':
    net = create_mobilenetv1_ssd(len(class_names), is_test=True)
elif args.net_type == 'mb1-ssd-lite':
    net = create_mobilenetv1_ssd_lite(len(class_names), is_test=True)
elif args.net_type == 'mb2-ssd-lite':
    net = create_mobilenetv2_ssd_lite(len(class_names), is_test=True)
elif args.net_type == 'sq-ssd-lite':
    net = create_squeezenet_ssd_lite(len(class_names), is_test=True)
else:
    print("The net type is wrong. It should be one of vgg16-ssd, mb1-ssd and mb1-ssd-lite.")
    sys.exit(1)
net.load(args.model_path)

if args.net_type == 'vgg16-ssd':
    predictor = create_vgg_ssd_predictor(net, candidate_size=200)
elif args.net_type == 'mb1-ssd':
    predictor = create_mobilenetv1_ssd_predictor(net, candidate_size=200)
elif args.net_type == 'mb1-ssd-lite':
    predictor = create_mobilenetv1_ssd_lite_predictor(net, candidate_size=200)
elif args.net_type == 'mb2-ssd-lite':
    predictor = create_mobilenetv2_ssd_lite_predictor(net, candidate_size=200)
elif args.net_type == 'sq-ssd-lite':
    predictor = create_squeezenet_ssd_lite_predictor(net, candidate_size=200)
else:
    predictor = create_vgg_ssd_predictor(net, candidate_size=200)


cap = cv2.VideoCapture(args.input)
if (cap.isOpened() == False): 
  print("Unable to read camera feed")
 
frame_width = int(cap.get(3))
frame_height = int(cap.get(4))

frameCount = 0
frameWait = 1400 # Wait this many frames before looking for next truck
frameFound = -frameWait

if args.show:
	cv2.namedWindow('Result', cv2.WINDOW_AUTOSIZE)
	cv2.moveWindow('Result', 0, 0)

# Output of recording file
out = None
fourcc = cv2.VideoWriter_fourcc(*'MPEG')
fgbg = cv2.createBackgroundSubtractorMOG2(300, 400, False)

recording = False
startedRecordingFrame = 0

MIN_BG_COUNT = 3000 # Minimum amount of pixels that need to be found in order to start recording
FRAMES_TO_RECORD = frameWait # Will record the next frames until

triggered = False # Allow only one trigger per application

def bgCheck(frame, ogframe):
	global recording
	global out
	
	# Get the foreground mask
	fgmask = fgbg.apply(frame)

	# Count all the non zero pixels within the mask
	count = np.count_nonzero(fgmask)

	print('Frame: %d, Pixel Count: %d' % (frameCount, count))

	if recording:
		# Stop recording
		if startedRecordingFrame > startedRecordingFrame + FRAMES_TO_RECORD:
			recording = False
		elif not args.no_record:
			out.write(ogframe)

	elif (frameCount > 1 and count > MIN_BG_COUNT):
		print('Starting to record')
		filename_root = 'records/trash-collect-' + datetime.datetime.now().strftime("%m-%d-%Y_%H-%M-%S") + '.avi'
		if not args.no_record:
			out = cv2.VideoWriter(filename_root, cv2.VideoWriter_fourcc('M','J','P','G'), 30, (frame_width, frame_height))
		recording = True
	
	return count > MIN_BG_COUNT

while True:
	(ret, frame) = cap.read()
	frameCount = frameCount + 1
	print('\n\nFrame', frameCount)

	if ret:
		# Start timer
		timer = cv2.getTickCount()

		ogframe = frame
		# image = ogframe
		image = cv2.resize(frame, (0, 0), fx=0.50, fy=0.50)
		
		# Only will run predictor if Background has changed enough. This saves on resources
		if bgCheck(image, ogframe):

			boxes, labels, probs = predictor.predict(image, 10, 0.4)
			Found = False

			for i in range(boxes.size(0)):
					box = boxes[i, :]
					label = f"{class_names[labels[i]]}: {probs[i]:.2f}"
					if probs[i] > .8: Found = True
					print(f"Probability: {probs[i]}")

					if args.show:
						cv2.rectangle(image, (int(box[0]), int(box[1])), (int(box[2]), int(box[3])), (255, 255, 0), 4)
						cv2.putText(image, label,
												(int(box[0]) + 20, int(box[1]) + 40),
												cv2.FONT_HERSHEY_SIMPLEX,
												1,  # font scale
												(255, 0, 255),
												2)  # line type

			if Found and frameCount > (frameFound + frameWait):
				print(f"Found {len(probs)} objects")
				frameFound = frameCount

				# Only runs truck simulation once per start
				if not triggered:
					print('Found garbage truck')
					found_garbage()
					triggered = True

		if args.show:
			cv2.imshow('Result', image)

			# k = cv2.waitKey(0 if args.manual or Found else 1) & 0xff
			k = cv2.waitKey(0 if args.manual else 1) & 0xff
			print('k %d' % k)
			# Escape key to exit
			if k == 27:
				break
		
		# Calculate Frames per second (FPS)
		fps = cv2.getTickFrequency() / (cv2.getTickCount() - timer)
		print('fps: ', fps)

cap.release()
cv2.destroyAllWindows()

