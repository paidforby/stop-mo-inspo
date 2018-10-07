var img;
var capture; 
var W = 1080, H = 720;
var i = 0, j = 0, k = 0;
var canvas;
var divisor = 10;
var stored_image = [];
var count = 0;
var still_frames = 4;
var zip = new JSZip();

var captutrer
var capturing = 0;

var gui;
var onion_skin = [];

var OnionSkin = function() {
  this.opacity = 0.8;
  this.image = undefined;
};


function setup(){

    canvas = createCanvas(W+W, H+(H/divisor));
    // uncomment to use HSC color mode, otherwise defaults to RGB
    //colorMode(HSB, 100);

    capture = createCapture(VIDEO);
    capture.size(W, H);
    capture.hide();
    
    gui = new dat.GUI(); //{ width: 350, autoPlace: false } );

    onion_skin[0] = new OnionSkin();
    onion_skin[1] = new OnionSkin();

    var f = gui.addFolder("onions");
    f.add(onion_skin[0], "opacity", 0, 255 ).listen();
    f.add(onion_skin[1], "opacity", 0, 255 ).listen();
    f.open();

    //capturer = new CCapture( { format: 'webm' } );
}

function draw(){

    //background(255);

    // display webcam feed
    image(capture, 0, 0, W, H); 

    // if space bar is pressed
    if(debounce(32, 200)){
        // capture frame from webcam
        stored_image[count] = get(0, 0, W, H);
        //var filename = "capture_"+count+".jpg";
        //zip.file("capture0", stored_image[count],  {base64: true});
        console.log(stored_image);
        image(stored_image[count], W-(W/divisor), H, W/divisor, H/divisor); 
        shiftImages();
        count++;
        //saveCanvas(canvas, 'frame', 'jpg')
    }

    // show onion skins once frames have been captured
    if(count >= 1){
        tint(255, onion_skin[0].opacity);
        image(stored_image[count-1], 0, 0, W, H); 
        if(count >= 2){
            tint(255, onion_skin[1].opacity);
            image(stored_image[count-2], 0, 0, W, H); 
        }
        tint(255, 255);
    }

    if(i == divisor){
        i = 0;
    }

    if(j == still_frames){
        j = 0;
        k++;
    }
    j++;
    if(k >= count){
        k = 0;
    }

    // display animate loop after capturing five frames
    if(count > 5){
        image(stored_image[k], W, 0 , W, H); 
        /*
        if(!capturing){
            capturer.start();
            capturing = 1;
        }else{
            capturer.capture( canvas );
        }
        */
    }
}

function mousePressed(){
    //capturer.stop();
    //capturer.save();
}

var previousTime = Date.now();

function debounce(key, timeout){
    var pressed = false;
    var currentTime = Date.now();
    if((currentTime - previousTime) > timeout){
        if(keyIsDown(key)){
            pressed = true;
            previousTime = currentTime;
        }
    }
    return pressed;
}

var small_image = [];
function shiftImages(){

    for(i = 0; i <= divisor; i++){
      small_image[i] = get(i*(W/divisor), H, W/divisor, H/divisor)  
      small_image[i-1] = small_image[i];
    }
    for(i = 0; i <= divisor; i++){
        image(small_image[i], i*(W/divisor), H, W/divisor, H/divisor); 
    }

}
