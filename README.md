# Prusa Raspberry Pi Camera

In this repository there are two scripts.
First script takes picutres with picamera2 python moduel and post to PrusaConnect on a loop, sleep delay is define in an enviormental variable.
Second script monitors the tempurature of the pi CPU and writes stats about the CPU to a CSV file. According to my testing, even though the cabinent that the printer and Raspberry is in would reach 35 deg C, the CPU would not exceed 61 deg C. The Rasperry Pi which I am using can operate at full performance up to 85 deg C CPU temp, after that the CPU gets trottled as a thermal protection.
Here is the BOM for the hardware I'm using:

- [Raspberry Pi 5] (https://www.raspberrypi.com/products/raspberry-pi-5/)
- [Raspberry Pi Active Cooler] (https://www.raspberrypi.com/products/active-cooler/)
- [Rasperry Pi Camera Module 3] (https://www.raspberrypi.com/products/camera-module-3/)
- [Raspberry Pi Camera Cable 300mm] (https://www.raspberrypi.com/products/camera-cable/)
- [Raspberry Pi 5 Metal Case Aluminum Alloy Shell] (https://www.aliexpress.com/item/1005006547436126.html)
- USB C PD/GaN powersupply, no less than 27 watt

I designed an printed a stand for the camery which you can find here: https://www.printables.com/model/881376-stand-for-raspberry-pi-camera-module-3

Software wise, boot your Raspberry Pi 5 up with latest [Raspberry Pi OS] (https://www.raspberrypi.com/software/), which was version 6.6 at the time of this writing. Grab the python scripts and run them. The included bash script, startcam.sh.sample will take care of that for you. Remove the .sample of the end of the filename and put your Prusa toke and camera fingerprint in the approiate variables, add execute permission to the shell script then execute and you are up and running.