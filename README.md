# stop-mo-inspo
inspiration for stop motion projects

This is now a python program for creating stop motion videos.   
Currently, it does the basics; 
- shows your current web cam feed or USB camera feed (set by changing `camera = cv2.VideoCapture(0)` to either 0 or 1) 
- captures a frame from camera by pressing spacebar, 
- shows a looped video of captured frames. 
- onion skinning (i.e. overlays of previous frames on current feed)
- saves captured frames in `frames` directory 

To get started, open terminal and execute the following commands:

1. Clone this repo with ```git clone https://github.com/paidforby/stop-mo-inspo``` 
2. Move into the repo with ```cd stop-mo-inspo``` or copy the contents in to a different folder
2. Install dependencies for python OpenCV (will add instructions or requirements.txt)
4. Run `python ./main.py`

Once you are happy with your animation, you can create a video from your captured frames by executing the following ffmpeg command within the frames directory,
```
ffmpeg -r 6 -i frame%04d.jpg -vcodec libx264 -crf 25 -pix_fmt yuv420p horse_in_motion.mp4
```
where `-r 6` specifies the frame rate or your animation

It is also great idea to backup the frames in a new folder by running something like,
```
cp -r frames horses_in_moition
```

Now start messing with the ```main.py``` file to modify the script being run.
