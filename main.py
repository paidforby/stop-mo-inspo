# import the necessary packages
from __future__ import print_function
#import numpy as np
import time
import cv2
 
cv2.namedWindow("preview")
cv2.namedWindow("animate")
camera = cv2.VideoCapture(1)

framerate = .0416 #float(1/24)
stillnumber = 4 

lastFrameTime = time.time()
 
print("Hey there ")

def callback(x):
    #a = cv2.getTrackbarPos("alpha", "preview")
    #print("alpha={}".format(a))
    pass

# Add a slider
cv2.createTrackbar("a", "preview", 0, 100, callback)

if camera.isOpened(): # try to get the first frame
    rval, frame = camera.read()
    count = 0
    order = 0 
    still = 0
else:
    rval = False

print(time.time() - lastFrameTime)

while rval:
    #alpha = .5
    rval, frame = camera.read()
    key = cv2.waitKey(20)

    #overlay = frame.copy()
    output = frame.copy()

    alpha = float(cv2.getTrackbarPos("a", "preview"))
    alpha = alpha/100

    if count > 0:
        previous_frame = "frames/frame" + str('{:04d}'.format(count-1)) + ".jpg"
        overlay = cv2.imread(previous_frame)
        #cv2.rectangle(overlay, (420, 205), (595, 385), (0, 0, 255), -1)
        #cv2.putText(overlay, "PyImageSearch: alpha={}".format(alpha), (10, 30), cv2.FONT_HERSHEY_SIMPLEX, 1.0, (0, 0, 255), 3)
        cv2.addWeighted(overlay, alpha, output, 1 - alpha, 0, output)
    
    if count > 5:
        if (time.time() - lastFrameTime) > framerate:
            framename = "frames/frame" + str('{:04d}'.format(order)) + ".jpg"
            img = cv2.imread(framename,1)
            cv2.imshow("animate", img) #display image
            still = still + 1
            if still > stillnumber:
                order = order + 1
                still = 0
            if order >= count:
                order = 0
            lastFrameTime = time.time()

    cv2.imshow("preview", output)

    if key == 32: # capture on SPACE 
        filename = "frames/frame" + str('{:04d}'.format(count)) + ".jpg"
        cv2.imwrite(filename, frame) #save image
        count = count + 1

    #if key == 13: # hold ENTER to playback frames 
    #    framename = "frames/frame" + str('{:04d}'.format(order)) + ".jpg"
    #    img = cv2.imread(framename,1)
    #    cv2.imshow("animate", img) #display image
    #    order = order + 1
    #    if order >= count:
    #        order = 0

    if key == 27: # exit on ESC
        break

cv2.destroyWindow("preview")
