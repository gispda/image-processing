import cv2
import numpy as np
#import time 
#import sys
#import imutils 


CANNY = 250

#for seeing if there are squares
isSquares = False 
MORPH = 7


cap = cv2.VideoCapture(0)


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


while True:
    # Take each frame
    _, frame = cap.read()
    
    # Convert RGB to HSV
    hsv = cv2.cvtColor(frame, cv2.COLOR_BGR2HSV)
        
    # Threshold the HSV image to get only color wanted
    maskBlue = cv2.inRange(hsv, lowerBlue, upperBlue)
    maskRed = cv2.inRange(hsv, lowerRed, upperRed)
    maskYellow = cv2.inRange(hsv, lowerYellow, upperYellow)
    
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
                (x,y,w,h) = cv2.boundingRect(approx)
                print("square looking headass ")
                isSquares = True
                pts_src = np.array( approx, np.float32 )
                h, status = cv2.findHomography( pts_src, pts_dst )
                out = cv2.warpPerspective( maskBlueBilateral, h, ( int( _width + _margin * 2 ), int( _height + _margin * 2 ) ) )
                cv2.drawContours( frame, [approx], -1, ( 255, 0, 0 ), 2 )
                cv2.putText(frame, 'blue square',(x,y),cv2.FONT_HERSHEY_SIMPLEX, 0.7, (255,0,0))


            else:
                pass 

        
    #Make frame tracking object
        
    #Display live video frame
    cv2.imshow('frame',frame)
    cv2.imshow('mask',maskBlue)

    cv2.imshow('Blue Object Edges', edgesBlue)
    if isSquares:
        cv2.imshow('output Squares', out)
        
    # Write frame to file
    #frame = cv2.flip(frame,0)
    if cv2.waitKey(5) == 27:
        break
def findShapes(colorMask,shapeArray,colorString):
    #color is the thing you want to find aka the mast
    #shape 
    #just find both shapes ? 
    edges  = cv2.Canny( colorMask , 10, CANNY )
    kernelShape = cv2.getStructuringElement( cv2.MORPH_RECT, ( MORPH, MORPH ) )
    closed = cv2.morphologyEx( edges, cv2.MORPH_CLOSE, kernelShape ) #fill in noisy spots
    _, contours, hierarchy = cv2.findContours( closed, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE )
    
    for cont in contours:
        area = cv2.contourArea(cont)
        if area > 300:
            arc_len = cv2.arcLength(cont,True)
            approx = cv2.approxPolyDP(cont, 0.1*arc_len, True)
            
            if(len(approx) ==4): #REMEMBER OR 
                (x,y,w,h) = cv2.boundingRect(approx)
                print("square")
                pts_src = np.array( approx, np.float32 )
                h, status = cv2.findHomography( pts_src, pts_dst )
                #out = cv2.warpPerspective( colorMask, h, ( int( _width + _margin * 2 ), int( _height + _margin * 2 ) ) )
                cv2.drawContours( frame, [approx], -1, ( 255, 0, 0 ), 2 )
                cv2.putText(frame, colorString +" square",(x,y),cv2.FONT_HERSHEY_SIMPLEX, 0.7, (255,0,0))

            elif(len(approx) == 3):
                print("found this triangle")
            else:
                pass 
        
    print("in function")
    
cap.release()
cv2.destroyAllWindows()