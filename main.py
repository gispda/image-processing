import cv2
import numpy as np
#import time 
#import sys
#import imutils 



#for seeing if there are squares
isSquares = False 

CANNY = 250
MORPH = 7


cap = cv2.VideoCapture(0)

#blue
BLUE = (0, 0, 255)
RED =  (255,0,0)


# Blue range \]
lowerBlue = np.array([100,100,100])
upperBlue = np.array([140,255,255])

# Red range
lowerRed = np.array([0,100,100])
upperRed = np.array([10,255,255])

#Yellow Range
lowerYellow = np.array([2,50,75])
upperYellow = np.array([100,100,200])


#dimensions of rect
_width  = 600.0
_height = 420.0
_margin = 0.0

#dimensions of rect 
corners = np.array(
	[
		[[ _margin, _margin ]],
		[[ 	_margin, _height + _margin]],
		[[ _width + _margin, _height + _margin]],
		[[ _width + _margin, _margin]],
	]

)

pts_dst = np.array( corners, np.float32 )

def findShapes(colorMask,COLOR, shapeLen, colorString,shapeString ):
    #color is the thing you want to find aka the mast
    #shape 
    #just find both shapes ? 
    colorMask = cv2.bilateralFilter(colorMask, 1,10,120)
    edges  = cv2.Canny( colorMask , 10, CANNY)
    _, contours, hierarchy = cv2.findContours( edges, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE )
    
    for cont in contours:
        area = cv2.contourArea(cont)
        if area > 300:
            arc_len = cv2.arcLength(cont,True)
            approx = cv2.approxPolyDP(cont, 0.1*arc_len, True)
            
            if(len(approx) ==shapeLen): #REMEMBER OR 
                print("found" + colorString + " " + shapeString)
                (x,y,w,h) = cv2.boundingRect(approx)
                cv2.drawContours( frame, [approx], -1, COLOR, 2 )
                cv2.putText(frame, colorString + " " + shapeString,(x,y),cv2.FONT_HERSHEY_SIMPLEX, 0.7, (255,0,0))

            else:
                pass 
        
    print("in function")
    
while True:
    # Take each frame
    _, frame = cap.read()
    
    # Convert RGB to HSV
    hsv = cv2.cvtColor(frame, cv2.COLOR_BGR2HSV)
        
    # Threshold the HSV image to get only color wanted
    maskBlue = cv2.inRange(hsv, lowerBlue, upperBlue)
    maskRed = cv2.inRange(hsv, lowerRed, upperRed)
    maskYellow = cv2.inRange(hsv, lowerYellow, upperYellow)
    
    #gotta make a black mask for finding Numbers
    
    colorArr = [maskBlue, maskRed, maskYellow]

    maskBlueBilateral = cv2.bilateralFilter(maskBlue,1,10,120)
    edgesBlue  = cv2.Canny( maskBlueBilateral , 10, CANNY )
    kernelShape = cv2.getStructuringElement( cv2.MORPH_RECT, ( MORPH, MORPH ) )
    closed = cv2.morphologyEx( edgesBlue, cv2.MORPH_CLOSE, kernelShape ) #fill in noisy spots
    _, blueContours, hierarchy = cv2.findContours( closed, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE )


   
    #get contours for square objects
    for cont in blueContours:
        area = cv2.contourArea(cont)
        if area > 300:
            arc_len = cv2.arcLength( cont, True ) #arc length
            approx = cv2.approxPolyDP(cont, 0.1 * arc_len, True)
            
            #c = max(cont, key=cv2.contourArea) #find the max contour 

            if(len(approx) ==4):
                print("square looking headass ")
                #SQUARES NOT WORKING BUT TRI IS PERFECT  

                (a,b,c,d) = cv2.boundingRect(approx)
                isSquares = True
                pts_src = np.array( approx, np.float32 )
                h, status = cv2.findHomography( pts_src, pts_dst )
                out = cv2.warpPerspective( maskBlueBilateral, h, ( int( _width + _margin * 2 ), int( _height + _margin * 2 ) ) )
                cv2.drawContours( frame, [approx], -1, ( 255, 0, 0 ), 2 )
                cv2.putText(frame, 'blue square',(a,b),cv2.FONT_HERSHEY_SIMPLEX, 0.7, (255,0,0))


            else:
                pass
    findShapes(maskRed,RED, 3,"red ","Triangle")
    #findShapes(maskBlue, "blue", 4, "square")
    

        
    #Make frame tracking object
        
    #Display live video frame
    cv2.imshow('frame',frame)
    cv2.imshow('mask',maskBlue)

    cv2.imshow('Blue Object Edges', edgesBlue)
#    if isSquares:
#        cv2.imshow('output Squares', out)
        
    # Write frame to file
    #frame = cv2.flip(frame,0)
    if cv2.waitKey(5) == 27:
        break

    
cap.release()
cv2.destroyAllWindows()