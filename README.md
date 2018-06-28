# stop-mo-inspo
inspiration for stop motion projects

This is a very rudimentary web app for creating stop motion videos. It does (or will do) the basics; show your current web cam feed, capture a frame from web cam by pressing space, show a timeline of previously captured frames, and show a looped "video" of captured frames. Hoping to add onion skinning (i.e. overlays of previous frames on current feed), more control options for playback, and some export options (ordered pics, full videos, self-contained gifs, etc).

To get started, open terminal and execute the following commands:

1. Clone this repo with ```git clone https://github.com/paidforby/stop-mo-inspo``` 
2. Move into the repo with ```cd p5-starter``` or copy the contents in to a different folder
3. Create local copies of the p5 libraries with ```./requirments.sh```
3. Start a webserver with ```python -m SimpleHTTPServer 8000``` or another preferred webserver
4. In a web browser, open http://localhost:8000
5. Capture frames by pressing (or holding) space bar.

Now start messing with the ```main.js``` file to modify the script being run.
