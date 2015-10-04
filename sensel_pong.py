#!/usr/bin/env python

##########################################################################
# Copyright 2015 Sensel, Inc.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
# 
# http://www.apache.org/licenses/LICENSE-2.0
# 
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
##########################################################################

#
#  Read Contacts
#  by Aaron Zarraga - Sensel, Inc
# 
#  This opens a Sensel sensor, reads contact data, and prints the data to the console.
#
#  Note: We have to use \r\n explicitly for print endings because the keyboard reading code
#        needs to set the terminal to "raw" mode.
##

from __future__ import print_function
from keyboard_reader import *
import sensel
import winsound
import sys
import pyaudio
import wave
import math
CHUNK = 1024

#230*120
#0,0 = 115, 60
exit_requested = False;


def findGrid (x,y):
    if ((((x-115)**2)+((y-100)**2))<1225):
        return 1
    if ((((x-182)**2)+((y-60)**2))<729):
        return 2
    if ((((x-48)**2)+((y-60)**2))<729):
        return 3
    else:
        return 4
    
    
def keypress_handler(ch):
    global exit_requested

    if ch == 0x51 or ch == 0x71: #'Q' or 'q'
        print("Exiting Example...", end="\r\n");
        exit_requested = True;


def openSensorReadContacts():
    sensel_device = sensel.SenselDevice()

    if not sensel_device.openConnection():
        print("Unable to open Sensel sensor!", end="\r\n")
        exit()

    keyboardReadThreadStart(keypress_handler)

    #Enable contact sending
    sensel_device.setFrameContentControl(sensel.SENSEL_FRAME_CONTACTS_FLAG)
  
    #Enable scanning
    sensel_device.startScanning()

    print("\r\nTouch sensor! (press 'q' to quit)...", end="\r\n")
    
    
    
    
    
    while not exit_requested: 
        contacts = sensel_device.readContacts()
  
        if len(contacts) == 0:
            continue
   
        for c in contacts:
            event = ""
            if c.type == sensel.SENSEL_EVENT_CONTACT_INVALID:
                event = "invalid"; 
            elif c.type == sensel.SENSEL_EVENT_CONTACT_START:
                sensel_device.setLEDBrightness(c.id, 100) #Turn on LED
                event = "start"
                if  (findGrid(c.x_pos_mm,c.y_pos_mm) !=4):
                    if (len(sys.argv) < 2):
                        print("Plays a wave file.\n\nUsage: %s filename.wav" % sys.argv[0])
                        sys.exit(-1)
                    wf = wave.open(sys.argv[1], 'rb')
                    p = pyaudio.PyAudio()
                    stream = p.open(format=p.get_format_from_width(wf.getsampwidth()),
                        channels=wf.getnchannels(), 
                        rate=wf.getframerate(),
                        output=True)
                    data = wf.readframes(CHUNK)
                    while data != '':
                        stream.write(data);
                        data = wf.readframes(CHUNK);
            elif c.type == sensel.SENSEL_EVENT_CONTACT_MOVE:
                event = "move";
            elif c.type == sensel.SENSEL_EVENT_CONTACT_END:
                sensel_device.setLEDBrightness(c.id, 0) #Turn off LED
                event = "end";
            else:
                event = "error";           
    stream.stop_stream()
    stream.close()
    sensel_device.stopScanning();
    sensel_device.closeConnection();
    keyboardReadThreadStop()

if __name__ == "__main__":
    openSensorReadContacts()
    
