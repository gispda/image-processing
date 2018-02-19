# -*- coding: utf-8 -*-
"""
Created on Sun Feb 18 18:09:08 2018

@author: catherine lee
"""

#script to run the shapedetector class

from pyimagesearch.shapedetector import ShapeDetector
import argparse
import imutils
import cv2 

#consruct argument parse and parse argumets

#NOTE: currently can only identify in images 
ap = argparse.ArgumentParser()
ap.add_argument("-1", "--image", required = True,
                help = "path to the input image")
args = vars(ap.parse_args())

#load image and resize, so shapes can be seen better
image = cv2.imread(args["image"])
resized = imutils.resize(image, width=300)
ratio = image.shape[0] / float(resized.shape[0])

#convert the resized image to grayscale
gray = cv2.cvtColor(resized,cv2.COLOR_BGR2GRAY)
blurred = cv2.GaussianBlur(gray, (5,5),0)
thresh = cv2.threshold(blurred,60.255, cv2.THRESH_BINARY)[1]