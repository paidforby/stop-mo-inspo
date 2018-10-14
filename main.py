import cv2

#cv2.namedWindow("preview")
#cv2.namedWindow("animate")
vc = cv2.VideoCapture(0)

if vc.isOpened(): # try to get the first frame
    rval, frame = vc.read()
    count = 0
    order = 0 
else:
    rval = False

while rval:
    cv2.imshow("preview", frame)
    rval, frame = vc.read()
    key = cv2.waitKey(20)
    if key == 32: # capture on SPACE 
        filename = "frames/frame" + str(count) + ".jpg"
        cv2.imwrite(filename, frame) #save image
        count = count + 1
    if key == 13: # hold ENTER to playback frames 
        framename = "frames/frame" + str(order) + ".jpg"
        img = cv2.imread(framename,1)
        cv2.imshow("animate", img) #display image
        order = order + 1
        if order >= count:
            order = 0
    if key == 27: # exit on ESC
        break
cv2.destroyWindow("preview")
