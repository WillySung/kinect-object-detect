#!/usr/bin/python

# Standard imports
import cv2
import numpy as np
import freenect

# Read image
#im = cv2.imread("blob.jpg", cv2.IMREAD_GRAYSCALE)
while True : 
	video,timestamp = freenect.sync_get_video()
	video = cv2.cvtColor(video,cv2.COLOR_RGB2BGR)

	# Setup SimpleBlobDetector parameters.
	params = cv2.SimpleBlobDetector_Params()

	# Change thresholds
	params.minThreshold = 10
	params.maxThreshold = 200


	# Filter by Area.
	params.filterByArea = True
	params.minArea = 1500

	# Filter by Circularity
	params.filterByCircularity = True
	params.minCircularity = 0.1

	# Filter by Convexity
	params.filterByConvexity = True
	params.minConvexity = 0.87
    
	# Filter by Inertia
	params.filterByInertia = True
	params.minInertiaRatio = 0.01

	# Create a detector with the parameters
	ver = (cv2.__version__).split('.')
	if int(ver[0]) < 3 :
		detector = cv2.SimpleBlobDetector(params)
	else : 
		detector = cv2.SimpleBlobDetector_create(params)


	# Detect blobs.
	#keypoints = detector.detect(im)
	keypoints = detector.detect(video)

	# Draw detected blobs as red circles.
	# cv2.DRAW_MATCHES_FLAGS_DRAW_RICH_KEYPOINTS ensures
	# the size of the circle corresponds to the size of blob

	#im_with_keypoints = cv2.drawKeypoints(im, keypoints, np.array([]), (0,0,255), cv2.DRAW_MATCHES_FLAGS_DRAW_RICH_KEYPOINTS)
	video_with_keypoints = cv2.drawKeypoints(video, keypoints, np.array([]), (0,0,255), cv2.DRAW_MATCHES_FLAGS_DRAW_RICH_KEYPOINTS)
	# Show blobs
	cv2.imshow("Keypoints", video_with_keypoints)
	k = cv2.waitKey(5) & 0xFF
        if k == 27: 
            break
cv2.destroyAllWindows()
