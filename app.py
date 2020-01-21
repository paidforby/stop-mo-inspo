# import the necessary packages
from __future__ import print_function
from stopmotionapp import StopMotionApp
#from imutils.video import VideoStream
import argparse
import time
 
# construct the argument parse and parse the arguments
ap = argparse.ArgumentParser()
ap.add_argument("-c", "--camera", type=int, default=0, help="which camera device should be used, corresponds to /dev/videoX")
ap.add_argument("-d", "--dslr", type=int, default=0, help="is the camera a supported DSLR device, 0 for no, 1 for yes")
args = vars(ap.parse_args())
 
# start the app
sma = StopMotionApp(args["camera"], args["dslr"])
sma.root.mainloop()
