# import the necessary packages
from __future__ import print_function
#import numpy as np
import time
import cv2
from easygui import *
import os
import re
import sys
import errno
import shutil
import subprocess
import tkinter as tk

camera_index = int(sys.argv[1])
is_dslr = int(sys.argv[2])

def dslr_setup():
    p = subprocess.Popen(['gphoto2 --stdout --capture-movie | gst-launch-1.0 fdsrc ! decodebin3 name=dec ! queue ! videoconvert ! v4l2sink device=/dev/video1'], shell=True, stdout=subprocess.PIPE, stderr=subprocess.STDOUT);

if is_dslr == 1:
    print("Setting up DSLR")
    dslr_setup()

project_dir = ""
msg = "Would you like to load a project or create a new one?"
choices = ["Load an existing project", "Start a new project", "Cancel"]
reply = buttonbox(msg, choices=choices)

if reply == choices[0]:

    # Delete any frames leftover from last run
    folder = './frames'
    pattern = 'frame*'
    for f in os.listdir(folder):
        if re.search(pattern, f):
            os.remove(os.path.join(folder, f))

    # Open a list of projects from projects directory
    root='./projects'
    title = "Load a project"
    dirlist = [ item for item in os.listdir(root) if os.path.isdir(os.path.join(root, item)) ]
    print(dirlist)
    entermsg = "Choose an existing project"
    choice = choicebox(entermsg, title, dirlist)

    # Copy frames from project directory to working directory
    project_dir = os.path.join(root, choice)
    framelist = [ item for item in os.listdir(project_dir) if os.path.isfile(os.path.join(project_dir, item)) ]
    for i in range(0, len(framelist)):
        shutil.copy2(os.path.join(project_dir, framelist[i]), "./frames/")
    
    # Set frame count to number of frames in project
    count = len(framelist)
    print("Count is ", count)

    pass
elif reply == choices[1]:
    folder = './frames'
    pattern = 'frame*'
    for f in os.listdir(folder):
        if re.search(pattern, f):
            os.remove(os.path.join(folder, f))
    count = 0
    pass
elif reply == choices[2]: 
    sys.exit(0)
else: 
    sys.exit(1)
 
cv2.namedWindow("preview")
cv2.namedWindow("animate")
camera = cv2.VideoCapture(camera_index)

framerate = .0416 #float(1/24)
stillnumber = 2 

lastFrameTime = time.time()
lastBlinkTime = time.time()
 
def alpha_callback(x):
    #a = cv2.getTrackbarPos("alpha", "preview")
    #print("alpha={}".format(a))
    pass

def blink_callback(x):
    pass

def rate_callback(x):
    pass

# Add a slider
cv2.createTrackbar("onion", "preview", 0, 100, alpha_callback)
cv2.createTrackbar("blink", "preview", 0, 100, blink_callback)
cv2.createTrackbar("timing", "animate", 2, 6, rate_callback)

if camera.isOpened(): # try to get the first frame
    rval, frame = camera.read()
    order = 0 
    still = 0
    blink_on = False 
    print("Camera connected at /dev/video" + str(camera_index))
else:
    rval = False
    print("Camera not found")

while rval:

    rval, frame = camera.read()
    key = cv2.waitKey(20)

    try:
        output = frame.copy()
    except:
        if is_dslr == 1:
            print("DSLR camera timed out. Resetting.")
            time.sleep(2) 
            dslr_setup()
        else:
            print("Failed to grab frame. Check camera connection.")


    alpha = float(cv2.getTrackbarPos("onion", "preview"))
    alpha = alpha/100

    blink = float(cv2.getTrackbarPos("blink", "preview"))
    blink = blink/40

    stillnumber = int(cv2.getTrackbarPos("timing", "animate"))

    if count > 0:
        previous_frame = "frames/frame" + str('{:04d}'.format(count-1)) + ".jpg"
        overlay = cv2.imread(previous_frame)

        if blink > 0: 
            if (time.time() - lastBlinkTime) > blink:
                blink_on = not blink_on
                lastBlinkTime = time.time()
            if blink_on:
                cv2.addWeighted(overlay, 1, output, 0, 0, output)

        else:
            cv2.addWeighted(overlay, alpha, output, 1 - alpha, 0, output)
    
    if count > 5:
        if (time.time() - lastFrameTime) > framerate:
            framename = "frames/frame" + str('{:04d}'.format(order)) + ".jpg"
            img = cv2.imread(framename,1)
            cv2.imshow("animate", img) #display image
            still = still + 1
            if still >= stillnumber:
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

    def save_as():
        msg = "Enter the name of your project"
        title = "Save your frames"
        fieldNames = ["Project Name"]
        fieldValues = []
        fieldValues = multenterbox(msg, title, fieldNames)
        while 1:
            if fieldValues == None: break
            errmsg = ""
            for i in range(len(fieldNames)):
                if fieldValues[i].strip() == "":
                    errmsg = errmsg + ('"%s" is a required field.\n\n' % fieldNames[i])
            if errmsg == "": break # no problems found 
            fieldValues = multenterbox(errmsg, title, fieldNames, fieldValues)
        print("Reply was:", fieldValues)
        directory = "./projects/" + fieldValues[0] + "/"
        return directory

    if key == 27: # exit on ESC
        msg = "Would you like to save the frames of your animation?"
        choices = ["Yes","No"]
        reply = buttonbox(msg, choices=choices)
        if reply == "Yes": 

            if project_dir == "":
                directory = save_as()
            else:
                msg = "Save"
                choices = ["Save and Close","Save as...","Cancel"]
                reply = buttonbox(msg, choices=choices)
                if reply == "Save and Close":
                    directory = project_dir
                elif reply == "Save as...":
                    msg = "Save as..."
                    choices = ["Overwrite...","Save as new project..."]
                    reply = buttonbox(msg, choices=choices)
                    if reply == "Overwrite...":
                        root='./projects'
                        title = "Save as..."
                        msg = "Overwrite an existing project"
                        dirlist = [ item for item in os.listdir(root) if os.path.isdir(os.path.join(root, item)) ]
                        choice = choicebox(msg, title, dirlist)
                        directory = "./projects/" + choice + "/"
                    elif reply == "Save as new project...":
                        directory = save_as()

                else:
                    sys.exit(0)

            # Copy frames to project directory
            if not os.path.exists(os.path.dirname(directory)):
                try:
                    os.makedirs(os.path.dirname(directory))
                except OSError as exc: # Guard against race condition
                    if exc.errno != errno.EEXIST:
                        raise
            for i in range(0, count):
                shutil.copy2("frames/frame" + str('{:04d}'.format(i)) + ".jpg", directory)
            pass 

        else:
            sys.exit(0)
        break

cv2.destroyWindow("preview")
