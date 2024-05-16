# Prusa Raspberry Pi Camera

In this repository there are two scripts.
First script takes picutres with picamera2 python moduel and post to PrusaConnect on a loop, sleep delay is define in an enviormental variable.
Second script monitors the tempurature of the pi CPU and writes stats about the CPU to a CSV file. According to my testing, even though the cabinent that the printer and Raspberry is in would reach 35 deg C, the CPU would not exceed 61 deg C. The Rasperry Pi which I am using can operate at full performance up to 85 deg C CPU temp, after that the CPU gets trottled as a thermal protection.

## Hardware

Here is the BOM for the hardware I'm using:

- [Raspberry Pi 5](https://www.raspberrypi.com/products/raspberry-pi-5/)
- [Raspberry Pi Active Cooler](https://www.raspberrypi.com/products/active-cooler/)
- [Rasperry Pi Camera Module 3](https://www.raspberrypi.com/products/camera-module-3/)
- [Raspberry Pi Camera Cable 300mm](https://www.raspberrypi.com/products/camera-cable/)
- [Raspberry Pi 5 Metal Case Aluminum Alloy Shell](https://www.aliexpress.com/item/1005006547436126.html)
- USB C PD/GaN powersupply, no less than 27 watt

I designed an printed a stand for the camery which you can find here: https://www.printables.com/model/881376-stand-for-raspberry-pi-camera-module-3

## Software

Software wise, boot your Raspberry Pi 5 up with latest [Raspberry Pi OS] (https://www.raspberrypi.com/software/), which was version 6.6 at the time of this writing. Grab the python scripts and run them. The included bash script, startcam.sh.sample will take care of that for you. Remove the .sample of the end of the filename and put your Prusa toke and camera fingerprint in the approiate variables, add execute permission to the shell script then execute and you are up and running. Make sure vcgencmd and requests python modules are installed first.

### prusacam.py

The main thing to beware for this script is to have the requests module installed and configure environment variables. Here are the variables used by this script.
```
export PRUSATOKEN=from-prusa-connect
export CAMFP=camera-finger-print
export CAMPIC=/tmp/prusaimg.jpg #File name for the picture
export CAMINT=5  # Number of seconds to to sleep between snapshots, plus 2 seconds
export SILENT=true # No output when true
```

## tempmon.py

This script requires the vcgencmd module and operates on command line parameters, not environment variables. Here are the parameters available:
```
siggib@raspberrypi3D:~/prusacam $ python tempmon.py --help
usage: tempmon.py [-h] [--silent] [--sleep SLEEP_TIME] [--filename FILE_NAME]

Raspberry Pi Monitor

options:
  -h, --help            show this help message and exit
  --silent              only output to file, not to screen
  --sleep SLEEP_TIME    Number of seconds to sleep inbetween checks, default is 60
  --filename FILE_NAME  Output file name, defaults to {scriptname}.csv in the script directory
siggib@raspberrypi3D:~/prusacam $
```
So if filename is specified it needs to be an absolute path. Otherwise if the script full path name is /var/prusacam/tempmon.py, and now is 16 may 2024 13:34:55, the full name for the output file will be /var/prusacam/tempmon-2024-05-16-13-34-55.csv