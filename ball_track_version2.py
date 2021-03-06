#Pakiety
from collections import deque
import numpy as np
import argparse
import imutils
import cv2
 

ap = argparse.ArgumentParser()
ap.add_argument("-v", "--video")
ap.add_argument("-b", "--buffer", type=int, default=64,
	help="max buffer size")
args = vars(ap.parse_args())
# okreslenie zakresu kolorow koloru pilki 
greenLower = (29, 86, 6)
greenUpper = (64, 255, 255)
pts = deque(maxlen=args["buffer"])
 
#brak video ==> wlaczenie kamery
if not args.get("video", False):
	camera = cv2.VideoCapture(0)
 
# otherwise, grab a reference to the video file
else:
	camera = cv2.VideoCapture(args["video"])
	
while True:
	
	(grabbed, frame) = camera.read()
 
	
	if args.get("video") and not grabbed:
		break
 
	# zmoien rozmiar klatki, uzyj rozmycia, przerob na  HSV
	# przestrzen koloru
	frame = imutils.resize(frame, width=600)
	blurred = cv2.GaussianBlur(frame, (11, 11), 0)
	hsv = cv2.cvtColor(frame, cv2.COLOR_BGR2HSV)
 
	# stwoorzenie maski dla koloru "zielonego"
	# erozja do usuniecia bledow
	
	mask = cv2.inRange(hsv, greenLower, greenUpper)
	mask = cv2.erode(mask, None, iterations=2)
	mask = cv2.dilate(mask, None, iterations=2)
		# znajdz kontury i wyznacz 
	# (x, y) srodek pilki
	cnts = cv2.findContours(mask.copy(), cv2.RETR_EXTERNAL,
		cv2.CHAIN_APPROX_SIMPLE)[-2]
	center = None
 
	if len(cnts) > 0:
		
		c = max(cnts, key=cv2.contourArea)
		((x, y), radius) = cv2.minEnclosingCircle(c)
		M = cv2.moments(c)
		center = (int(M["m10"] / M["m00"]), int(M["m01"] / M["m00"]))
 
		# rozmiar promienia 
		if radius > 10:
			#narysuj srodek i sledz punkty
			cv2.circle(frame, (int(x), int(y)), int(radius),
				(0, 255, 255), 2)
			cv2.circle(frame, center, 5, (0, 0, 255), -1)
 
	#aktualizuj kolejke punktow
	pts.appendleft(center)
		
	for i in xrange(1, len(pts)):
	
		if pts[i - 1] is None or pts[i] is None:
			continue
 
		#oblicz grubosc lini
		thickness = int(np.sqrt(args["buffer"] / float(i + 1)) * 2.5)
		cv2.line(frame, pts[i - 1], pts[i], (0, 0, 255), thickness)
 
	# pokaz klatke - frame
	cv2.imshow("Frame", frame)
	key = cv2.waitKey(1) & 0xFF
 
	# "q" zatrzymuje petle
	if key == ord("q"):
		break
 
# cleanup the camera and close any open windows
camera.release()
cv2.destroyAllWindows()