#!/usr/bin/python3
import io
import threading, os, signal
import picamera
import logging
import socketserver
from select import select
from threading import Condition
from http import server
import subprocess
from subprocess import check_call, call
import sys
import glob
import Rpi.GPIO as GPIO

# Define the pin
GPIO.setmode(GPIO.BOARD)
IR=11
Flash=13
Stream=29
Capture=33
Shutdown=40
GPIO.setup(IR, GPIO.OUT)
GPIO.setup(Flash, GPIO.OUT)
GPIO.setup(Stream, GPIO.IN, pull_up_down = GPIO.PUD_UP)
GPIO.setup(Capture, GPIO.IN, pull_up_down = GPIO.PUD_UP)
GPIO.setup(Shutdown, GPIO.IN, pull_up_down = GPIO.PUD_UP)

ipath = "/home/pi/Documents/Thesis_2206_live.py"    #CHANGE THIS PATH TO THE LOCATION OF live.py

def thread_second():
    call(["python3", ipath])

def check_kill_process(pstring):
    for line in os.popen("ps ax | grep " + pstring + " | grep -v grep"):
        fields = line.split()
        print(fields)
        pid = fields[0]
        print(pid)
        os.kill(int(pid), signal.SIGKILL)

# run script continuosly
while True:

    if GPIO.input(Capture)==0:
        # end livestream
        check_kill_process('live.py')
        print("Stream ended.")

        # get last image number in usb drive
        pictures = glob.glob('/home/pi/*.jpg')     #CHANGE PATH TO YOUR USB THUMBDRIVE
        # default picture number to zero
        picNum = 0

        # determine the picture number
        if not pictures == []:
            numPics = len(pictures)
            lastPic = pictures[numPics-1]
            lastPicData = lastPic.split('/')
            sudoLen = len(lastPicData)
            jpgFile = lastPicData[sudoLen-1]
            jpgData = jpgFile.split('.')
            picNum = jpgData[0]
            picNum = int(picNum) + 1
        else:
            picNum = 1

        # take picture with camera
        with picamera.PiCamera() as camera:
            #change resolution to get better latency
            camera.resolution = (640,480)

            #Turn off the IR light, Turn on the Flash light and capture image
            GPIO.output(IR, False)
            sleep(1)
            GPIO.output(Flash, True)
            sleep(1)
            camera.capture("/home/pi" + str(picNum) + ".jpg")     #CHANGE PATH TO YOUR USB THUMBDRIVE
            GPIO.output(Flash, False)
        # alert picture taken
        print("Picture taken: " + str(picNum) + ".jpg")

    if GPIO.input(Stream) == 0:
        # run live stream again ==> Stream button
        processThread = threading.Thread(target=thread_second)
        processThread.start()
        print("Stream running. Refresh page.")

    # when middle mouse button is pressed, shutdown raspberry pi ==> Tunr off button
    if GPIO.input(Shutdown)==0:
        call("sudo nohup shutdown -h now", shell=True)
        print("Shutting down...")

        break

# print in the command line instead of file's cons
if __name__ == '__main__':
    main()
