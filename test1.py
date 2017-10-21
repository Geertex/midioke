# -*- coding: utf-8 -*-
"""
Created on Sat Oct 21 13:23:03 2017

@author: dead
"""

import pyaudio
import wave
import numpy as np
print("It is Recording.....")
print("If you want to stop just press 'Ctrl + C' ")

CHUNK = 1024
FORMAT = pyaudio.paInt16
CHANNELS = 2
RATE = 44100
RECORD_SECONDS = 5
WAVE_OUTPUT_FILENAME = "output.wav"

p = pyaudio.PyAudio()

stream = p.open(format=FORMAT,
                channels=CHANNELS,
                rate=RATE,
                input=True,
                frames_per_buffer=CHUNK)

print("* recording")

frames = []

try:
    while True:
        data = stream.read(CHUNK)
        frames.append(data)
        #print(np.mean(data))        
except KeyboardInterrupt:
    pass



#==============================================================================
# for i in range(0, int(RATE / CHUNK * RECORD_SECONDS)):
#     data = stream.read(CHUNK)
#     frames.append(data)
#     print(np.mean(data))
#==============================================================================

print("* done recording")

stream.stop_stream()
stream.close()
p.terminate()

wf = wave.open(WAVE_OUTPUT_FILENAME, 'wb')
wf.setnchannels(CHANNELS)
wf.setsampwidth(p.get_sample_size(FORMAT))
wf.setframerate(RATE)
wf.writeframes(b''.join(frames))
wf.close()