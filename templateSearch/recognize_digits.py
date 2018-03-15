# -*- coding: utf-8 -*-
"""
Created on Wed Feb 28 18:03:33 2018

@author: catherine
"""

# import the necessary packages
from imutils.perspective import four_point_transform
import imutils 
import cv2
import numpy as np

 
# define the dictionary of digit segments so we can identify
# each digit on the thermostat
black = np.array([0,0,0])

DIGITS_LOOKUP = {
	(1, 1, 1, 0, 1, 1, 1): 0,
	(0, 0, 1, 0, 0, 1, 0): 1,
	(1, 0, 1, 1, 1, 1, 0): 2,
	(1, 0, 1, 1, 0, 1, 1): 3,
	(0, 1, 1, 1, 0, 1, 0): 4,
	(1, 1, 0, 1, 0, 1, 1): 5,
	(1, 1, 0, 1, 1, 1, 1): 6,
	(1, 0, 1, 0, 0, 1, 0): 7,
	(1, 1, 1, 1, 1, 1, 1): 8,
	(1, 1, 1, 1, 0, 1, 1): 9
}
# load the example image

cap = cv2.VideoCapture(0)

while(True):
    _, frame = cap.read()
    hsv = cv2.cvtColor(frame,cv2.COLOR_BGR2HSV)
    black = cv2.inRange(hsv, black, black )
    blurred = cv2.GaussianBlur(black, (5,5,), 0 )
    edged = cv2.Canny(blurred, 50, 200, 255)
    #thresh = cv2.threshold(warped, 0, 255, cv2.THRESH_BINARY_INV | cv2.THRESH_OTSU)
    contours = cv2.findContours(edged.copy(), cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
    
    digits = []
    
    # extract the thermostat display, apply a perspective transform
    # to it
    warped = four_point_transform(black, displayCnt.reshape(4, 2))
    output = four_point_transform(image, displayCnt.reshape(4, 2))
    # threshold the warped image, then apply a series of morphological
    # operations to cleanup the thresholded image
    thresh = cv2.threshold(warped, 0, 255, cv2.THRESH_BINARY_INV | cv2.THRESH_OTSU)[1]
    kernel = cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (1, 5))
    thresh = cv2.morphologyEx(thresh, cv2.MORPH_OPEN, kernel)
    
    for cnts in contours:
        (x,y,w,h) = cv2.boundingRect(cnts)
        roi = thresh[y:y + h, x:x + w]
        (roiH, roiW) = roi.shape
        (dW, dH) = (int(roiW * 0.25), int(roiH * 0.15))
        dHC = int(roiH * 0.05)        
        segments = [
    		((0, 0), (w, dH)),	# top
    		((0, 0), (dW, h // 2)),	# top-left
    		((w - dW, 0), (w, h // 2)),	# top-right
    		((0, (h // 2) - dHC) , (w, (h // 2) + dHC)), # center
    		((0, h // 2), (dW, h)),	# bottom-left
    		((w - dW, h // 2), (w, h)),	# bottom-right
    		((0, h - dH), (w, h))	# bottom
    	]
        on = [0] * len(segments)
        
    	# loop over the segments
        for (i, ((xA, yA), (xB, yB))) in enumerate(segments):
    		# extract the segment ROI, count the total number of
    		# thresholded pixels in the segment, and then compute
    		# the area of the segment
            segROI = roi[yA:yB, xA:xB]
            total = cv2.countNonZero(segROI)
            area = (xB - xA) * (yB - yA)
     
    		# if the total number of non-zero pixels is greater than
    		# 50% of the area, mark the segment as "on"
            if total / float(area) > 0.5:
                on[i]= 1
     
    	# lookup the digit and draw it on the image
        digit = DIGITS_LOOKUP[tuple(on)]
        digits.append(digit)
        cv2.rectangle(frame, (x, y), (x + w, y + h), (0, 255, 0), 1)
        cv2.putText(frame, str(digit), (x - 10, y - 10),
    		cv2.FONT_HERSHEY_SIMPLEX, 0.65, (0, 255, 0), 2)     
        if cv2.waitKey(5) == 27:
            break
        
    
# display the digits
print(u"{}{}.{} \u00b0C".format(*digits))
cv2.imshow("edges", edged)

cap.release()
cv2.destroyAllWindows()