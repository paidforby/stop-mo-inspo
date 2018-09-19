#!/bin/sh

mkdir libs
cd libs
wget https://cdnjs.cloudflare.com/ajax/libs/p5.js/0.6.0/p5.js
wget https://cdnjs.cloudflare.com/ajax/libs/p5.js/0.6.0/addons/p5.dom.js
wget https://cdnjs.cloudflare.com/ajax/libs/p5.js/0.6.0/addons/p5.sound.js
wget https://cdnjs.cloudflare.com/ajax/libs/dat-gui/0.6.5/dat.gui.min.js

git clone https://github.com/spite/ccapture.js -b v1.0.9
cp ccapture.js/src/* .
