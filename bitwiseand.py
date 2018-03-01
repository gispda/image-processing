import cv2
import numpy as np

CANNY =10

cap=cv2.VideoCapture(0)
lower_red = np.array([0,100,100])
upper_red = np.array([10,255,255])


lowerBlue = np.array([100,100,100])
upperBlue = np.array([140,255,255])
while True:
    _, frame=cap.read()
   
    hsv=cv2.cvtColor(frame,cv2.COLOR_BGR2HSV)



    mask=cv2.inRange(hsv,lowerBlue,upperBlue)
    
    res=cv2.bitwise_and(frame,frame, mask=mask)
    
    edges  = cv2.Canny( res , 10, CANNY )
    _, contours, hierarchy = cv2.findContours( edges, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE )
    for cont in contours:
        area = cv2.contourArea(cont)
        if area > 300:
            arc_len = cv2.arcLength( cont, True ) #arc length
            approx = cv2.approxPolyDP(cont, 0.1 * arc_len, True)
            
            #c = max(cont, key=cv2.contourArea) #find the max contour 

            if(len(approx) ==3):
                #SQUARES NOT WORKING BUT TRI IS PERFECT  
                print("issa triangle")
                (x,y,w,h) = cv2.boundingRect(approx)
                cv2.drawContours(frame, [approx], -1, (255,0,0), 2)
                cv2.putText(frame, 'blue triangle', (x,y), cv2.FONT_HERSHEY_SIMPLEX,0.7,(255,0,0))

    
    cv2.imshow('frame',frame)
    cv2.imshow('mask', mask)
    cv2.imshow('res', res)

    k=cv2.waitKey(5)& 0xFF
    if k==27:
        break
        
cv2.destroyAllWindows()
cap.release()
