var img;
var capture; 
var W = 1080, H = 720;
var i = 0, j = 0, k = 0;
var canvas;
var divisor = 10;
var stored_image = [];
var count = 0;
var still_frames = 4;

function setup(){

    canvas = createCanvas(W+W, H+(H/divisor));
    // uncomment to use HSC color mode, otherwise defaults to RGB
    //colorMode(HSB, 100);

    // uncomment to enable webcam feed
    capture = createCapture(VIDEO);
    capture.size(W, H);
    capture.hide();

    //img = loadImage('assets/test.jpg');  
}

function draw(){

    //background(255);

    //image(capture, i*(W/10), j*(H/10), W/10, H/10); 
    image(capture, 0, 0, W, H); 

    if(debounce(32, 200)){
        stored_image[count] = get(0, 0, W, H);
        console.log(stored_image);
        image(stored_image[count], W-(W/divisor), H, W/divisor, H/divisor); 
        shiftImages();
        count++;
        //saveCanvas(canvas, 'frame', 'jpg')
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

    console.log(k);

    if(count > 5){
        image(stored_image[k], W, 0 , W, H); 
    }

    //image(img, 0, 0, W, H);

    fill(0, 102, 153);
    textSize(32);
    textAlign(LEFT);
    text('HELLO P5', 50, 50);

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
