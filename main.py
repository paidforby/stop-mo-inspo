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
import signal
import psutil 
import tkinter as tk

# GLOBAL VARIABLES
camera_index = int(sys.argv[1]) # corresponds to /dev/videoX
is_dslr = int(sys.argv[2]) # option to enable DSLR settings
project_dir = "" # stores name/directory of active project
count = 0 # number of frames in current animation
camera = "" # stores camera object
framerate = .0416 #float(1/24) i.e. 24fps
blink_on = False  # whether or not blinking in enabled, off by default
timing = 2 # timing of frames, i.e. shooting "on ones" or "on twos", on twos is default
capturing = False # whether or not camera is currently capturing a frame

# NOTE these state varibales need to be handled differently
order = 0 # index of current frame in animation
hold = 0 # index of frame within timing
lastFrameTime = time.time() # timing for animation loop
lastBlinkTime = time.time() # timing for blink loop

def alpha_callback(x):
    pass

def blink_callback(x):
    pass

def timing_callback(x):
    pass

def get_alpha():
    alpha = float(cv2.getTrackbarPos("onion", "preview"))
    alpha = alpha/100
    return alpha

def get_blink():
    blink = float(cv2.getTrackbarPos("blink", "preview"))
    blink = blink/40
    return blink

def get_timing():
    timing = int(cv2.getTrackbarPos("timing", "animate"))
    return timing

def dslr_setup():
    subprocess.Popen(['gphoto2 --stdout --capture-movie | gst-launch-1.0 fdsrc ! decodebin3 name=dec ! queue ! videoconvert ! v4l2sink device=/dev/video1'], shell=True, stdout=subprocess.PIPE, stderr=subprocess.STDOUT);

def dslr_kill():
    # Kill DSLR live feed quickly by killing gst launch
    subprocess.Popen(['pkill gst-launch-1.0'], shell=True);

def dslr_capture():
    subprocess.Popen(['gphoto2 --capture-image-and-download'], shell=True)

def save_as_prompt():
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

def save_to(directory):
    if not os.path.exists(os.path.dirname(directory)):
        try:
            os.makedirs(os.path.dirname(directory))
        except OSError as exc: # Guard against race condition
            if exc.errno != errno.EEXIST:
                raise
    for i in range(0, count):
        shutil.copy2("frames/frame" + str('{:04d}'.format(i)) + ".jpg", directory)

def check_dslr():
    if is_dslr == 1:
        print("Setting up DSLR")
        dslr_setup()

def clear_frame_dir():
    # Delete any frames leftover from last run
    folder = './frames'
    pattern = 'frame*'
    for f in os.listdir(folder):
        if re.search(pattern, f):
            os.remove(os.path.join(folder, f))

def choose_project(root, title):
    dirlist = [ item for item in os.listdir(root) if os.path.isdir(os.path.join(root, item)) ]
    print(dirlist)
    msg = "Choose an existing project"
    choice = choicebox(msg, title, dirlist)
    return choice

def copy_frames(p_dir):
    framelist = [ item for item in os.listdir(p_dir) if os.path.isfile(os.path.join(p_dir, item)) ]
    for i in range(0, len(framelist)):
        shutil.copy2(os.path.join(p_dir, framelist[i]), "./frames/")
    return len(framelist)

def start_window(c):
    msg = "Would you like to load a project or create a new one?"
    choices = ["Load an existing project", "Start a new project", "Cancel"]
    reply = buttonbox(msg, choices=choices)
    if reply == choices[0]:

        # Open a list of projects from projects directory
        root='./projects'
        title="Load an existing project"
        name = choose_project(root, title)

        # Set project directory to selected project
        p_dir = os.path.join(root, name)

        # Copy frames from project directory to working directory, return count of frames
        c = copy_frames(p_dir)
        print(c, "frames loaded")
        pass

    elif reply == choices[1]:
        # If new project, set count to zero and leave project dir blank for now
        c = 0
        p_dir = ""
        pass
    elif reply == choices[2]: 
        # If cancel, exit with 0
        sys.exit(0)
    else: 
        # If anything else, exit with 1
        sys.exit(1)
    return p_dir, c
 
def create_main_windows():
    cv2.namedWindow("preview")
    cv2.namedWindow("animate")

    # Add sliders
    cv2.createTrackbar("onion", "preview", 0, 100, alpha_callback)
    cv2.createTrackbar("blink", "preview", 0, 100, blink_callback)
    cv2.createTrackbar("timing", "animate", 2, 6, timing_callback)

def animate():
    # Animate window logic
    global lastFrameTime, order, hold
    if (time.time() - lastFrameTime) > framerate:
       framename = "frames/frame" + str('{:04d}'.format(order)) + ".jpg"
       img = cv2.imread(framename,1)
       cv2.imshow("animate", img) #display image
       hold = hold + 1
       if hold >= timing:
           order = order + 1
           hold = 0
       if order >= count:
           order = 0
       lastFrameTime = time.time()

def preview(output):
    # Add Blink or Onion Skin overlay
    global lastBlinkTime, blink_on
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
    # Sends output to preview window
    cv2.imshow("preview", output)

def capture(frame, c):
    filename = "frames/frame" + str('{:04d}'.format(c)) + ".jpg"
    cv2.imwrite(filename, frame) #save image
    c = c + 1
    return c

def on_exit(p_dir):
    msg = "Would you like to save the frames of your animation?"
    choice_one = ["Yes","No"]
    reply = buttonbox(msg, choices=choice_one)
    if reply == choice_one[0]: 
        if p_dir == "":
            directory = save_as_prompt()
        else:
            msg = "Save"
            choice_two = ["Save and Close","Save as...","Cancel"]
            reply = buttonbox(msg, choices=choice_two)
            if reply == choice_two[0]:
                directory = p_dir
            elif reply == choice_two[1]:
                msg = "Save as..."
                choice_three = ["Overwrite existing...","Save as new project..."]
                reply = buttonbox(msg, choices=choice_three)
                if reply == choice_three[0]:
                    root='./projects'
                    title = "Overwrite an existing project"
                    name = choose_project(root, title)
                    project_dir = os.path.join(root, name)
                elif reply == choice_three[1]:
                    directory = save_as_prompt()
            elif reply == choice_two[3]:
                sys.exit(0)
            else:
                sys.exit(1)
        save_to(directory)
    
    return 0


# Begin main program
check_dslr()
clear_frame_dir()
project_dir, count = start_window(count) # updates project directory and count if loading a project
create_main_windows()

# Initialize camera
camera = cv2.VideoCapture(camera_index)
#camera.set(cv2.CAP_PROP_FRAME_WIDTH, 1280)
#camera.set(cv2.CAP_PROP_FRAME_HEIGHT, 720)
if camera.isOpened(): # try to get the first frame
    rval, frame = camera.read()
    print("Camera connected at /dev/video" + str(camera_index))
else:
    rval = False
    print("Camera not found")

# Enter main program loop
while True:
    if capturing:
        rval, frame = camera.read()
        count = capture(frame, count)
        # if using DSLR, save high-res image
        if is_dslr==1:
            dslr_kill()
            dslr_capture()
            time.sleep(5) # sleeps needed to let camera respond to reset
            camera.release()
            time.sleep(5)
            dslr_setup()
            time.sleep(2)
            camera = cv2.VideoCapture(camera_index)
        capturing = False 
    elif rval:
        # Watch for keyboard press with 20ms debounce?
        key = cv2.waitKey(20)

        # Get values from trackbars
        alpha = get_alpha() 
        blink = get_blink()
        timing = get_timing()

        # Get live feed from camera
        rval, frame = camera.read()
        try:
            output = frame.copy()
        except:
            if capturing:
                print("capturing image, please wait")
            elif is_dslr == 1:
                print("DSLR camera timed out. Resetting.")
                time.sleep(2) 
                dslr_setup()
                time.sleep(2) 
            else:
                print("Failed to grab frame. Check camera connection.")

        if count == 0:
            # Just show preview before any frames are captured
            cv2.imshow("preview", output)
        else:
            # Begin normal operation once one frame is captured
            preview(output)
            animate() 

        if key == 32: # capture on SPACE 
            capturing = True

        if key == 27: # exit on ESC
            exit = on_exit(project_dir) 
            if exit == 0:
                break
            else:
                sys.exit(1)
    else:
        print("Error: camera connection lost")
        msg = "Connection to camera lost"
        choice = ["Try again","Save and Exit","Exit without Saving"]
        reply = buttonbox(msg, choices=choice)
        if reply==choice[0]:
            # Need logic to reconnect camera
            pass
        elif reply==choice[1]:
            on_exit(project_dir)
        elif reply==choice[2]:
            break
        else:
            sys.exit(1)    

        break

cv2.destroyWindow("preview")
cv2.destroyWindow("animate")
camera.release()
if is_dslr == 1:
    dslr_kill()
