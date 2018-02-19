# -*- coding: utf-8 -*-
"""
Created on Sun Feb 18 17:18:32 2018

@author: Catherine Lee
"""

#using opencv to identify shapes
import cv2

class ShapeDetector: 
    def __init__(self):
        pass
    def detect(self, c): #c is the contour of the shape we are attempting to identify
        shape = "unidentified"
        peri = cv2.arcLength(c, True) #computing perimeter of contour
        approx = cv2.approxPolyDP(c, 0.04*peri, True) #contour approx for reducing the number of points in a curve with reduced set of points 
        
        
        if len(approx) == 3: #if 3 vertices, identify shape as triangle 
            shape = "triangle"
        elif len(approx) == 4:
            #if 4 vertices, either square or rectangle
            #attempting to compute the aspect ratio to see if it is a square or rect
            
            (x,y,w,h) = cv2.boundingRect(approx)
            ar = w / float(h) #ar = aspect ratio
            
            if ar >= 0.95 and ar <= 1.05:
                shape = "square"
            else:
                shape = "rectangle"
                
        # TODO : ADD ONE FOR TRAPEZOID FFFFS
        elif len(approx) == 5:
            shape = "pentagon"
            
        return shape 
            
            
            
            