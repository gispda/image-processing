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

def adjust_gamma():
    print("TBD")

def findTri(colorMask,COLOR, colorString ):
    #Function to search for triangles by color
    
    #applies a filter to reduce noise
    #ideally find one that works well underwater 
    colorMask = cv2.bilateralFilter(colorMask, 1,10,120)
    
    #edges/outlines objects of specified color
    edges  = cv2.Canny( colorMask , 10, CANNY)
    
    #shows the frame for triangle edges
    cv2.imshow(colorString+ ' triangle edges',edges)

    _, contours, hierarchy = cv2.findContours( edges, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE )
    
    for cont in contours:
        area = cv2.contourArea(cont)
        if area > 200:
            arc_len = cv2.arcLength(cont,True)
            approx = cv2.approxPolyDP(cont, 0.1*arc_len, True)
            
            #if len == 3, then it is a triangle
            if(len(approx) ==3): #REMEMBER OR 
                print("found " + colorString + " triangle")
                (x,y,w,h) = cv2.boundingRect(approx)
                
                #draws contour if triangle is identified
                cv2.drawContours( frame, [approx], -1, (0,0,0), 2 )
                cv2.putText(frame, colorString + " triangle",(x,y),cv2.FONT_HERSHEY_SIMPLEX, 0.7, COLOR)

            else:
                pass 
        
def findRect(colorMask, COLOR, colorString):
    colorMask = cv2.bilateralFilter(colorMask,1,10,120)
    edges = cv2.Canny(colorMask,10,CANNY)
    kernelShape = cv2.getStructuringElement( cv2.MORPH_RECT, ( MORPH, MORPH ) )
    closed = cv2.morphologyEx( edges, cv2.MORPH_CLOSE, kernelShape ) #fill in noisy spots

    cv2.imshow(colorString+ ' rect edges',edges)
    _, contours, hierarchy = cv2.findContours(closed, cv2.RETR_EXTERNAL,cv2.CHAIN_APPROX_SIMPLE)
    
    for cont in contours:
        area = cv2.contourArea(cont)
        if area > 200: #maybe change the area here
            arc_len = cv2.arcLength(cont, True)
            approx = cv2.approxPolyDP(cont, 0.1 * arc_len, True)
            
            #c = max(cont, key=cv2.contourArea) #find the max contour 

            if(len(approx) ==4):
                #THIS SHIT DOES NOT WORK YET 
                (x,y,w,h) = cv2.boundingRect(approx)
                print("found " + colorString + " rectangle")
                pts_src = np.array( approx, np.float32 )
                h, status = cv2.findHomography( pts_src, pts_dst )
                out = cv2.warpPerspective( colorMask, h, ( int( _width + _margin * 2 ), int( _height + _margin * 2 ) ) )
                cv2.drawContours( frame, [approx], -1, ( 0, 0, 0 ), 2 )
                cv2.putText(frame, colorString + ' square',(x,y),cv2.FONT_HERSHEY_SIMPLEX, 0.7, COLOR)

            else:
                pass 
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
    

#    maskBlueBilateral = cv2.bilateralFilter(maskBlue,1,10,120)
#    edgesBlue  = cv2.Canny( maskBlueBilateral , 10, CANNY )
#    kernelShape = cv2.getStructuringElement( cv2.MORPH_RECT, ( MORPH, MORPH ) )
#    closed = cv2.morphologyEx( edgesBlue, cv2.MORPH_CLOSE, kernelShape ) #fill in noisy spots
#    _, blueContours, hierarchy = cv2.findContours( closed, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE )
#
#
#   
#    #get contours for square objects
#    for cont in blueContours:
#        area = cv2.contourArea(cont)
#        if area > 300:
#            arc_len = cv2.arcLength( cont, True ) #arc length
#            approx = cv2.approxPolyDP(cont, 0.1 * arc_len, True)
#            
#            #c = max(cont, key=cv2.contourArea) #find the max contour 
#
#            if(len(approx) ==4):
#                print("square looking headass ")
#                #SQUARES NOT WORKING BUT TRI IS PERFECT  
#
#                (a,b,c,d) = cv2.boundingRect(approx)
#                isSquares = True
#                pts_src = np.array( approx, np.float32 )
#                h, status = cv2.findHomography( pts_src, pts_dst )
#                out = cv2.warpPerspective( maskBlueBilateral, h, ( int( _width + _margin * 2 ), int( _height + _margin * 2 ) ) )
#                cv2.drawContours( frame, [approx], -1, ( 255, 0, 0 ), 2 )
#                cv2.putText(frame, 'blue square',(a,b),cv2.FONT_HERSHEY_SIMPLEX, 0.7, (255,0,0))
#
#            elif(len(approx) ==3):
#                (x,y,w,h) = cv2.boundingRect(approx)
#                cv2.drawContours(frame,[approx],-1,(255,0,0),2)
#                cv2.putText(frame, 'blue tri', (x,y), cv2.FONT_HERSHEY_SIMPLEX,0.7,(255,0,0))
#            else:
#                pass
    findRect(maskRed,RED,"red ")
    findRect(maskBlue, BLUE, "blue")
    findRect(maskYellow, YELLOW,"yellow")

    findTri(maskRed,RED,"red ")
    
    findTri(maskBlue, BLUE, "blue")
    
    findTri(maskYellow,YELLOW,"yellow")    

    #findShapes(maskBlue, "blue", 4, "square")
    

        
    #Make frame tracking object
        
    #Display live video frame
    cv2.imshow('frame',frame)
    cv2.imshow('blue mask',maskBlue)
    cv2.imshow('red mask', maskRed)
    cv2.imshow('yellow mask', maskYellow)
    
#    if isSquares:
#        cv2.imshow('output Squares', out)
        
    # Write frame to file
    #frame = cv2.flip(frame,0)
    
    #Press ESC to exit 
    if cv2.waitKey(5) == 27:
        break

    
cap.release()
cv2.destroyAllWindows()
