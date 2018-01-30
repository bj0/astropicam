# Setup:

## fbcp 

Kivy can only draw to the GPU, which cannot be displayed on the pitft.  To see the display, we must use **fbcp**.

get it from:

    git clone git://github.com/tasanakorn/rpi-fbcp
    
then build it with:

    cd rpi-fbcp
    mkdir build
    cd build
    cmake ..
    

## DISPLAY=:0

Without **DISPLAY** set, Kivy cannot find a display to use.

## RPi_Cam_Web_Interface

If the web interface is running, it will have control of the camera and any camera commands will fail.  Use the `start` and `stop` scripts in the downloaded installer directory.



# Running:

It is easiest to run from **byobu**, one term can run `fbcp` and one can run `python -m picam`