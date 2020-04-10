
from multiprocessing import Manager
from multiprocessing import Process
from imutils.video import VideoStream
from pyimagesearch.objcenter import ObjCenter
from pyimagesearch.pid import PID
import pantilthat as pth
import argparse
import signal
import time
import sys
import cv2

servoRange = (-90, 90)

def signal_handler(sig, frame):
	print("[INFO] You pressed `ctrl + c`! Exiting...")
	pth.servo_enable(1, False)
	pth.servo_enable(2, False)
	sys.exit()

def obj_center(args, objX, objY, centerX, centerY):
	signal.signal(signal.SIGINT, signal_handler)
	vs = VideoStream(usePiCamera=True).start()
	time.sleep(2.0)
	obj = ObjCenter(args["cascade"])

	while True:
		frame = vs.read()
		frame = cv2.flip(frame, 0)
		(H, W) = frame.shape[:2]
		centerX.value = W // 2
		centerY.value = H // 2
		objectLoc = obj.update(frame, (centerX.value, centerY.value))
		((objX.value, objY.value), rect) = objectLoc
		if rect is not None:
			(x, y, w, h) = rect
			cv2.rectangle(frame, (x, y), (x + w, y + h), (0, 255, 0),
				2)

		cv2.imshow("Pan-Tilt Face Tracking", frame)
		cv2.waitKey(1)

def pid_process(output, p, i, d, objCoord, centerCoord):
	signal.signal(signal.SIGINT, signal_handler)
	p = PID(p.value, i.value, d.value)
	p.initialize()

	while True:
		error = centerCoord.value - objCoord.value
		output.value = p.update(error)

def in_range(val, start, end):
	return (val >= start and val <= end)

def set_servos(pan, tlt):
	signal.signal(signal.SIGINT, signal_handler)

	while True:
		panAngle = -1 * pan.value
		tltAngle = -1 * tlt.value
		if in_range(panAngle, servoRange[0], servoRange[1]):
			pth.pan(panAngle)
		if in_range(tltAngle, servoRange[0], servoRange[1]):
			pth.tilt(tltAngle)

if __name__ == "__main__":
	ap = argparse.ArgumentParser()
	ap.add_argument("-c", "--cascade", type=str, required=True,
		help="path to input Haar cascade for face detection")
	args = vars(ap.parse_args())

	with Manager() as manager:
		pth.servo_enable(1, True)
		pth.servo_enable(2, True)
		centerX = manager.Value("i", 0)
		centerY = manager.Value("i", 0)

		objX = manager.Value("i", 0)
		objY = manager.Value("i", 0)

		pan = manager.Value("i", 0)
		tlt = manager.Value("i", 0)

		panP = manager.Value("f", 0.09)
		panI = manager.Value("f", 0.08)
		panD = manager.Value("f", 0.002)

		tiltP = manager.Value("f", 0.11)
		tiltI = manager.Value("f", 0.10)
		tiltD = manager.Value("f", 0.002)

		processObjectCenter = Process(target=obj_center,
			args=(args, objX, objY, centerX, centerY))
		processPanning = Process(target=pid_process,
			args=(pan, panP, panI, panD, objX, centerX))
		processTilting = Process(target=pid_process,
			args=(tlt, tiltP, tiltI, tiltD, objY, centerY))
		processSetServos = Process(target=set_servos, args=(pan, tlt))

		processObjectCenter.start()
		processPanning.start()
		processTilting.start()
		processSetServos.start()
		processObjectCenter.join()
		processPanning.join()
		processTilting.join()
		processSetServos.join()
		pth.servo_enable(1, False)
		pth.servo_enable(2, False)