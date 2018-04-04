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

    # member variables ############################################################################
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

###################################################################################################
arr = ["test1.png","test2.jpg","test3.jpg","test4.jpg","test5.jpg","test6.jpg"]

def fuckThis(image):
    allContoursWithData = []                # declare empty lists,
    validContoursWithData = []              # we will fill these shortly

    try:
        npaClassifications = np.loadtxt("classifications.txt", np.float32)                  # read in training classifications
    except:
        os.system("pause")
        return
    # end try

    try:
        npaFlattenedImages = np.loadtxt("flattened_images.txt", np.float32)                 # read in training images
    except:

        os.system("pause")
        return
    # end try

    npaClassifications = npaClassifications.reshape((npaClassifications.size, 1))       # reshape numpy array to 1d, necessary to pass to call to train

    kNearest = cv2.ml.KNearest_create()                   # instantiate KNN object

    kNearest.train(npaFlattenedImages, cv2.ml.ROW_SAMPLE, npaClassifications)

    imgTestingNumbers = cv2.imread(image)          # read in testing numbers image

    # end if

    
    #cv2.imshow("gray", imgGray)
    imgBlurred = cv2.GaussianBlur(imgTestingNumbers, (5,5), 0)                    # blur

                                                        # filter image from grayscale to black and white
    imgThresh = cv2.adaptiveThreshold(imgBlurred, 255, cv2.ADAPTIVE_THRESH_GAUSSIAN_C, cv2.THRESH_BINARY_INV,   11, 2)              #REMINDER: ADAPTIVE THRESHOLD REQUIRES GRAYSCALE!!!!!!!!!!!                    

    imgThreshCopy = imgThresh.copy()        # make a copy of the thresh image, this in necessary b/c findContours modifies the image

    _, npaContours, hierarchy = cv2.findContours(imgThreshCopy,             # input image, make sure to use a copy since the function will modify this image in the course of finding contours
                                                 cv2.RETR_EXTERNAL,         # retrieve the outermost contours only
                                                 cv2.CHAIN_APPROX_SIMPLE)   # compress horizontal, vertical, and diagonal segments and leave only their end points

    for npaContour in npaContours:                             # for each contour
        contourWithData = ContourWithData()                                             # instantiate a contour with data object
        contourWithData.npaContour = npaContour                                         # assign contour to contour with data
        contourWithData.boundingRect = cv2.boundingRect(contourWithData.npaContour)     # get the bounding rect
        contourWithData.calculateRectTopLeftPointAndWidthAndHeight()                    # get bounding rect info
        contourWithData.fltArea = cv2.contourArea(contourWithData.npaContour)           # calculate the contour area
        allContoursWithData.append(contourWithData)                                     # add contour with data object to list of all contours with data
    # end for

    for contourWithData in allContoursWithData:                 # for all contours
        if contourWithData.checkIfContourIsValid():             # check if valid
            validContoursWithData.append(contourWithData)       # if so, append to valid contour list
        # end if
    # end for

    validContoursWithData.sort(key = operator.attrgetter("intRectX"))         # sort contours from left to right

    strFinalString = ""         # declare final string, this will have the final number sequence by the end of the program

    for contourWithData in validContoursWithData:            # for each contour
                                                # draw a green rect around the current char
        cv2.rectangle(imgTestingNumbers,                                        # draw rectangle on original testing image
                      (contourWithData.intRectX, contourWithData.intRectY),     # upper left corner
                      (contourWithData.intRectX + contourWithData.intRectWidth, contourWithData.intRectY + contourWithData.intRectHeight),      # lower right corner
                      (0, 255, 0),              # green
                      2)                        # thickness

        imgROI = imgThresh[contourWithData.intRectY : contourWithData.intRectY + contourWithData.intRectHeight,     # crop char out of threshold image
                           contourWithData.intRectX : contourWithData.intRectX + contourWithData.intRectWidth]

        imgROIResized = cv2.resize(imgROI, (RESIZED_IMAGE_WIDTH, RESIZED_IMAGE_HEIGHT))             # resize image, this will be more consistent for recognition and storage

        npaROIResized = imgROIResized.reshape((1, RESIZED_IMAGE_WIDTH * RESIZED_IMAGE_HEIGHT))      # flatten image into 1d numpy array

        npaROIResized = np.float32(npaROIResized)       # convert from 1d numpy array of ints to 1d numpy array of floats

        retval, npaResults, neigh_resp, dists = kNearest.findNearest(npaROIResized, k = 1)     # call KNN function find_nearest

        strCurrentChar = str(chr(int(npaResults[0][0])))                                             # get character from results

        strFinalString = strFinalString + strCurrentChar            # append current char to full string
    # end for
    print(strFinalString)

    cv2.imshow("imgTestingNumbers", imgTestingNumbers)      # show input image with green boxes drawn around found digits
    cv2.waitKey(0)                                          # wait for user key press

    cv2.destroyAllWindows()             # remove windows from memory

    return

###################################################################################################
#for elem in arr:
#    fuckThis(elem)
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

        npaROIResized = imgROIResized.reshape((1, RESIZED_IMAGE_WIDTH * RESIZED_IMAGE_HEIGHT))      # flatten image into 1d numpy array

        npaROIResized = np.float32(npaROIResized)       # convert from 1d numpy array of ints to 1d numpy array of floats

        retval, npaResults, neigh_resp, dists = kNearest.findNearest(npaROIResized, k = 1)     # call KNN function find_nearest

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
    









