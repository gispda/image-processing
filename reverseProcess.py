import cv2
import numpy as np
#import time 
#import sys
#import imutils 



#for seeing if there are squares

#turns out we don't need to do both ocr and shape detection!!!! Can choose the side we want, but if we bump into the shape and destroy it, we are FUCKEDDDDD
isSquares = False 

CANNY = 250
MORPH = 7


cap = cv2.VideoCapture(0) #1 for the webcam on usb

#blue
BLUE = (255, 0, 0)
RED =  (0,0,255)
YELLOW = (0,255,255)


#NOTE: THESE ARE IN HSV 
# Blue range 
lowerBlue = np.array([110,100,100])
upperBlue = np.array([130,255,255])

# Red range
lowerRed = np.array([0,100,100])
upperRed = np.array([10,255,255])

#Yellow Range
lowerYellow = np.array([20,100,100])
upperYellow = np.array([50,255,255])



while True:
    # Take each frame
    _, frame = cap.read()
    
    edges = cv2.Canny(frame, 10,250)
    _,contours, hierarchy = cv2.findContours(edges, cv2.RETR_EXTERNAL,cv2.CHAIN_APPROX_SIMPLE)
    
    for cont in contours:
        area = cv2.contourArea(cont)
        if area > 400: 
            arc_len = cv2.arcLength(cont, True)
            approx = cv2.approxPolyDP(cont, 0.1*arc_len, True)
            
            if(len(approx) ==4):
                (x,y,w,h) = cv2.boundingRect(approx)
                print("found rect")
            elif(len(approx) ==4):
                print("found triangle")

    

    #Make frame tracking object
        
    #Display live video frame
    cv2.imshow('frame',frame)
    
#    if isSquares:
#        cv2.imshow('output Squares', out)
        
    # Write frame to file
    #frame = cv2.flip(frame,0)
    
    #Press ESC to exit 
    if cv2.waitKey(5) == 27:
        break

    
cap.release()
cv2.destroyAllWindows()
