# stop-mo-inspo
inspiration for stop motion projects

This is a python program for creating stop motion animations.  
Currently, it does the basics;   
- shows your current web cam feed or USB camera feed
- captures a frame from camera by pressing spacebar, 
- shows a looped video of captured frames. 
- onion skinning (i.e. overlays of previous frames on current feed)
- blinks between previous frame and current feed
- saves captured frames in a unique project directory upon exiting the program

To get started, open terminal and execute the following commands:

1. Clone this repo with ```git clone https://github.com/paidforby/stop-mo-inspo``` 
2. Move into the repo with ```cd stop-mo-inspo``` or copy the contents in to a different folder
2. Install dependencies (inside of a virtualenv is recommended)  
```
sudo apt install python3-tk
virtualenv .env  
source .env/bin/activate
pip install opencv-python
```
4. Run `python3 app.py --camera 0 --dslr 0`

The two arguments after `main.py` represent the index of the camera you would like to use (avaible devices can be found by running ```ls /dev/video*```) and whether or not you are using a DSLR-style camera (`0` for no, `1` for yes) which may require additional setup. See below for more info on that.  

To use a non-webcam camera such as a Nikon DS3200, you'll need trick your computer (assuming you are on an Ubuntu 18.04 machine) into thinking your DSLR camera is a webcam. First, connect your camera to your computer using a USB cable and then follow these steps:  
```
sudo apt-get install gphoto2 v4l2loopback-utils
sudo modprobe v4l2loopback
killall gvfs-gphoto2-volume-monitor
gphoto2 --stdout --capture-movie | gst-launch-1.0 fdsrc ! decodebin3 name=dec ! queue ! videoconvert ! v4l2sink device=/dev/video1
```
The last line as well as additional failsafe exceptions are included in `main.py` if your enter `1` as the second argument when running the program.  

If it doesn't work, make sure your camera is not loaded as a storage device by "ejecting it" from your file explorer.  
For a description and discussion on what these lines are doing, check out the source, https://askubuntu.com/questions/856460/using-a-digital-camera-canon-as-webcam  

Once you are happy with your animation, you can create a video from your captured frames by executing the following ffmpeg command within a project directory,  
```
ffmpeg -r 12 -i frame%04d.jpg -vcodec libx264 -crf 25 -pix_fmt yuv420p horse_in_motion.mp4
```
where `-r 12` specifies the frame rate or your animation. `-r 12` means that your frame rate is 12 frames per second. Assuming you are shooting "on twos" (i.e. each frame holds for two frames), you need half of the typical frame rate of 24 frames per second, that is 12. If you are shooting "on ones", then you can set `-r 24`. Likewise, if shooting "on fours", your theoretical frame rate is 6 frames per second, so `-r 6`.  

It is also great idea to backup the frames in a new folder by running something like,  
```
cp -r frames horses_in_moition
```

Now start messing with the ```stopmotionapp.py``` file to modify the script being run.  

The interaction between OpenCV and Tkinter was adpated from Adrian Rosebrock's Photobooth App, https://www.pyimagesearch.com/2016/05/30/displaying-a-video-feed-with-opencv-and-tkinter/

GPLv3 grant gallo 
