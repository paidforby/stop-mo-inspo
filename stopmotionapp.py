# import the necessary packages
from __future__ import print_function
from PIL import Image
from PIL import ImageTk
import tkinter as tki
import threading
import datetime
import imutils
import cv2
import os
import time
import subprocess
from tkinter import filedialog as fd
import re
import shutil

class StopMotionApp:
    def __init__(self, index, is_dslr):
        # store the video stream object and output path, then initialize
        # the most recently read frame, thread for reading frames, and
        # the thread stop event
        self.clear_frame_dir("./frames/")
        self.camera_index = index
        self.is_dslr = is_dslr
        print("[INFO] Connecting to camera at /dev/video" + str(self.camera_index))
        if self.is_dslr == 1:
            self.dslr_setup()
            time.sleep(2.0)
        self.vs = cv2.VideoCapture(self.camera_index)
        time.sleep(2.0)
        self.outputPath = "./frames"
        self.frame = None
        self.thread = None
        self.stopEvent = None
        self.count = 0
        self.saving = False
        self.opening = False
        self.project_dir = None

        self.lastBlinkTime = time.time()
        self.blink_on = False 

        self.lastFrameTime = time.time()
        self.order = 0
        self.hold = 0
        self.timing = 2
        self.framerate = .0416

        # initialize the root window and image panel
        self.root = tki.Tk()
        self.preview_panel = None
        self.animate_panel = None

        # Create sliders for onion-skinning, blinking, and control of timing
        self.onion = tki.Scale(self.root, from_=0, to=100, orient=tki.HORIZONTAL, tickinterval=10, label="Onion Skinning")
        self.onion.grid(row=1, column=0, sticky=tki.W+tki.E)

        self.blink = tki.Scale(self.root, from_=0, to=100, orient=tki.HORIZONTAL, tickinterval=10, label="Blinking")
        self.blink.grid(row=2, column=0, sticky=tki.W+tki.E)

        self.on_time = tki.Scale(self.root, from_=1, to=6, orient=tki.HORIZONTAL, tickinterval=1, label="On")
        self.on_time.grid(row=1, column=1, sticky=tki.W+tki.E)
        self.on_time.set(self.timing)

        # create a button, that when pressed, will take the current frame and save it
        btn = tki.Button(self.root, text="Capture Frame", command=self.capture)
        btn.grid(row=3, column=0)
        self.root.bind('<space>', self.capture)

        btn2 = tki.Button(self.root, text="Open Project", command=self.open_project)
        btn2.grid(row=3, column=1)

        btn3 = tki.Button(self.root, text="Save as...", command=self.save_as)
        btn3.grid(row=4, column=1)

        btn3 = tki.Button(self.root, text="Save", command=self.save)
        btn3.grid(row=5, column=1)

        # start a thread that constantly pools the video sensor for the most recently read frame
        self.stopEvent = threading.Event()
        self.thread = threading.Thread(target=self.videoLoop, args=())
        self.thread.start()

        # set a callback to handle when the window is closed
        self.root.wm_title("StopMoInspo")
        self.root.wm_protocol("WM_DELETE_WINDOW", self.onClose)

    def videoLoop(self):
        # keep looping over frames until we are instructed to stop
        while not self.stopEvent.is_set():
            # grab the frame from the video stream and resize it to have a maximum width of 640 pixels
            rval, self.frame = self.vs.read()
            #self.frame = imutils.resize(self.frame, width=640)

            # if both panels are None, we need to initialize them 
            # this is done here and not in init because of threading?
            if self.preview_panel is None and self.animate_panel is None:
                # swap color channels from BRGA to RBGA
                image = cv2.cvtColor(self.frame, cv2.COLOR_BGRA2RGBA)
                image = Image.fromarray(image)
                image = ImageTk.PhotoImage(image)
                self.preview_panel = tki.Label(image=image)
                self.preview_panel.image = image
                self.preview_panel.grid(row=0, column=0, padx=10, pady=10)
                self.animate_panel = tki.Label(image=image)
                self.animate_panel.image = image
                self.animate_panel.grid(row=0, column=1, padx=10, pady=10)

            # otherwise, if camera is available, perform preview and animation logic
            elif rval is True:
                if self.saving is False and self.opening is False:
                    self.preview()
                    self.animation()

            # otherwise, try to reconnect camera
            else: 
                if self.is_dslr==1:
                    print("[INFO] Trying to reconnect DSLR camera")
                    self.vs.release()
                    self.dslr_setup()
                    time.sleep(2)
                    self.vs = cv2.VideoCapture(self.camera_index)
                    time.sleep(2)
                else: 
                    print("[ERROR] Video disconnected")
                

    def capture(self, _event=None):
        #save image to frames directory
        filename = "frames/frame" + str('{:04d}'.format(self.count)) + ".jpg"
        cv2.imwrite(filename, self.frame.copy())
        if self.is_dslr==1:
            self.dslr_kill()
            self.dslr_capture()
            self.dslr_move()

        self.count = self.count + 1
        print("[INFO] saved {}".format(filename))

    def preview(self):
        # if a single capture has been taken, allow onion-skinning or blinking
        output = self.frame.copy()
        if self.count > 0:
            previous_frame = "frames/frame" + str('{:04d}'.format(self.count-1)) + ".jpg"
            overlay = cv2.imread(previous_frame)
            if overlay.shape == output.shape:
                alpha = float(self.onion.get())/100
                blink = float(self.blink.get())/40
                if blink > 0: 
                    if (time.time() - self.lastBlinkTime) > blink:
                        self.blink_on = not self.blink_on
                        self.lastBlinkTime = time.time()
                    if self.blink_on:
                        cv2.addWeighted(overlay, 1, output, 0, 0, output)
                else:
                    cv2.addWeighted(overlay, alpha, output, 1 - alpha, 0, output)
            else:
                print("[ERROR] previous frame " + previous_frame + " is not the same shape as current video feed /dev/video" + self.camera_index)

        # Sends output to preview window
        preview_img = cv2.cvtColor(output, cv2.COLOR_BGRA2RGBA)
        preview_img = Image.fromarray(preview_img)
        preview_img = ImageTk.PhotoImage(image=preview_img) 

        # update the panel
        self.preview_panel.configure(image=preview_img)
        self.preview_panel.image = preview_img

    def animation(self):
        if (time.time() - self.lastFrameTime) > self.framerate and self.count > 0:
            # Load next image in animation
            framename = "frames/frame" + str('{:04d}'.format(self.order)) + ".jpg"
            animate_img = cv2.imread(framename)
            if animate_img is not None:
                animate_img = cv2.cvtColor(animate_img, cv2.COLOR_BGRA2RGBA)
                animate_img = Image.fromarray(animate_img)
                animate_img = ImageTk.PhotoImage(image=animate_img) 

                # update the panel
                self.animate_panel.configure(image=animate_img)
                self.animate_panel.image = animate_img
            
            # Logic for progressing through frames in orderly fashion
            self.timing = self.on_time.get()
            self.hold = self.hold + 1
            if self.hold >= self.timing:
                self.order = self.order + 1
                self.hold = 0
            if self.order >= self.count:
                self.order = 0
            self.lastFrameTime = time.time()

    def dslr_setup(self):
        print("[INFO] Setting up DSLR")
        subprocess.Popen(['gphoto2 --stdout --capture-movie | gst-launch-1.0 fdsrc ! decodebin3 name=dec ! queue ! videoconvert ! v4l2sink device=/dev/video1'], shell=True, stdout=subprocess.PIPE, stderr=subprocess.STDOUT);

    def dslr_kill(self):
        # Kill DSLR live feed quickly by killing gst launch
        p1 = subprocess.Popen(['pkill gst-launch-1.0'], shell=True);
        p1.wait()

    def dslr_capture(self):
        p2 = subprocess.Popen(['gphoto2 --capture-image-and-download'], shell=True)
        p2.wait();

    def dslr_move(self):
        for filename in os.listdir('.'):
            root, ext = os.path.splitext(filename)
            if root.startswith('DSC') and ext == '.JPG':
                old_file = filename
        new_file = "frames_HQ/frame" + str('{:04d}'.format(self.count)) + ".jpg"
        os.rename(old_file, new_file)

    def clear_frame_dir(self, folder):
        # Delete any frames leftover from last run
        pattern = 'frame*'
        for f in os.listdir(folder):
            if re.search(pattern, f):
                os.remove(os.path.join(folder, f))

    def open_project(self):
        self.opening = True
        # TODO add checks that project is valid
        self.project_dir = fd.askdirectory(initialdir = "./projects",title = "Open an exisitng project")
        if self.project_dir is not None:
            self.clear_frame_dir("./frames/")
            self.count = self.copy_frames(self.project_dir)
        self.opening = False

    def copy_frames(self, p_dir):
        framelist = [ item for item in os.listdir(p_dir) if os.path.isfile(os.path.join(p_dir, item)) ]
        for i in range(0, len(framelist)):
            shutil.copy2(os.path.join(p_dir, framelist[i]), "./frames/")
        return len(framelist)
    
    def save_as(self):
        self.saving = True
        self.project_dir = fd.asksaveasfilename(initialdir = "./projects",title = "Save project as ...")
        if self.project_dir is not None:
            print(self.project_dir)
            self.save()
        self.saving = False

    def save(self):
        directory = self.project_dir
        if directory is None:
            self.save_as()

        else:
            if not os.path.exists(directory):
                try:
                    os.makedirs(directory)
                except OSError as exc: # Guard against race condition
                    if exc.errno != errno.EEXIST:
                        raise
            for i in range(0, self.count):
                shutil.copy2("frames/frame" + str('{:04d}'.format(i)) + ".jpg", directory)

    def onClose(self):
        # set the stop event, cleanup the camera, and allow the rest of
        # the quit process to continue
        print("[INFO] closing...")
        self.dslr_kill()
        self.stopEvent.set()
        self.vs.release()
        self.root.quit()
