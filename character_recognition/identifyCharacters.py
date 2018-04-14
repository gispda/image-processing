# identifyCharacters.py

import cv2
import numpy as np
import operator
import os


MIN_CONTOUR_AREA = 100
isSquare = False


RESIZED_IMAGE_WIDTH = 20
RESIZED_IMAGE_HEIGHT = 30

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

class ContourWithData():

    # member variables
    npaContour = None           # contour
    boundingRect = None         # bounding rect for contour
    intRectX = 0                # bounding rect top left corner x location
    intRectY = 0                # bounding rect top left corner y location
    intRectWidth = 0            # bounding rect width
    intRectHeight = 0           # bounding rect height
    fltArea = 0.0               # area of contour

    def calculateRectTopLeftPointAndWidthAndHeight(self):               # calculate bounding rect info
        [intX, intY, intWidth, intHeight] = self.boundingRect
        self.intRectX = intX
        self.intRectY = intY
        self.intRectWidth = intWidth
        self.intRectHeight = intHeight

    def checkIfContourIsValid(self):                            # this is oversimplified, for a production grade program
        if self.fltArea < MIN_CONTOUR_AREA: return False        # much better validity checking would be necessary
        return True



cap = cv2.VideoCapture(0)

def process(frame):
    allContoursWithData = []
    validContoursWithData = []
    
    frame = cv2.cvtColor(frame,cv2.COLOR_BGR2GRAY)
    classifications =  np.loadtxt("classifications.txt", np.float32)
    flattened = np.loadtxt("flattened_images.txt", np.float32)
    classifications = classifications.reshape((classifications.size, 1))       
    
    kNearest = cv2.ml.KNearest_create()
    
    kNearest.train(classifications,cv2.ml.ROW_SAMPLE,flattened)
    
    imgThresh = cv2.adaptiveThreshold(frame, 255, cv2.ADAPTIVE_THRESH_GAUSSIAN_C, cv2.THRESH_BINARY_INV, 11, 2)       
    
    imgThreshCopy = imgThresh.copy()
    
    _, npaContours, hierarchy = cv2.findContours(imgThreshCopy, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
    
    for npaContour in npaContours: #draw contours in the already reduced image
        contourWithData = ContourWithData() 
        contourWithData.npaContour = npaContour
        contourWithData.boundingRect = cv2.boundingRect(contourWithData.npaContour)
        contourWithData.calculateRectTopLeftPointAndWidthAndHeight()
        contourWithData.fltArea = cv2.contourArea(contourWithData.npaContour)
        allContoursWithData.append(contourWithData)
        
    for contourWithData in allContoursWithData:
        if contourWithData.checkIfContourIsValid():
            validContoursWithData.append(contourWithData) #check if contour is an appropriate size 
            
    validContoursWithData.sort(key = operator.attrgetter("intRectX"))         # sort contours from left to right
    
    finalString = ""
    
    for conts in validContoursWithData:
        cv2.rectangle(frame, (contourWithData.intRectX, conts.intRectY),
        (conts.intRectX + conts.intRectWidth,conts.intRectY + conts.intRectHeight),
        (0,255,0), 2)
        imgROI = imgThresh[conts.intRectY : conts.intRectY + conts.intRectHeight,     # crop char out of threshold image
                           conts.intRectX : conts.intRectX + conts.intRectWidth]
        imgROIResized = cv2.resize(imgROI, (RESIZED_IMAGE_WIDTH, RESIZED_IMAGE_HEIGHT))             # resize image, this will be more consistent for recognition and storage
        print(imgROIResized.shape);
        npaROIResized = imgROIResized.reshape((1, RESIZED_IMAGE_WIDTH * RESIZED_IMAGE_HEIGHT))      # flatten image into 1d numpy array
        #print(npaROIResized.shape); 
         

        npaROIResized = np.float32(npaROIResized)       # convert from 1d numpy array of ints to 1d numpy array of floats

        retval, npaResults, neighbors, dists = kNearest.findNearest(npaROIResized, k = 5)     # call KNN function find_nearest
    
    
        strCurrentChar = str(chr(int(npaResults[0][0])))       
        finalString = finalString + strCurrentChar     
    print(finalString)         
        

    
    print("in process")

while True:
    _,frame = cap.read() 
    #gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)

    edges = cv2.Canny(frame,10, 250)

    #first find edges 
    
    #fuckThis(frame)
    
    _, contours, hierarchy = cv2.findContours( edges, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE )
    
    for cont in contours:
        area = cv2.contourArea(cont)
        if area > 200:
            arc_len = cv2.arcLength(cont,True)
            approx = cv2.approxPolyDP(cont, 0.1*arc_len, True)
            if(len(approx) ==4):
                (x,y,w,h) = cv2.boundingRect(approx)
                isSquare = True
                pts_src = np.array( approx, np.float32 )
                #error w findhomography ???
                h, status = cv2.findHomography( pts_src, pts_dst )
                out = cv2.warpPerspective( frame, h, ( int( _width + _margin * 2 ), int( _height + _margin * 2 ) ) )
                
                
                process(out)
                

                #start the buffer 
                
            else:
                pass
                
            

    
    cv2.imshow("frame", frame)
    cv2.imshow("edges" ,edges)
    #cv2.imshow("gray",gray)
    #cv2.imshow("thresholded", threshed)
    if isSquare:
        cv2.imshow("out", out)


    if cv2.waitKey(5) == 27:
        break
        

        
cap.release() 
cv2.destroyAllWindows()
    









