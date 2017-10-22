# -*- coding: utf-8 -*-
"""
Created on a Sunday

@author: G-man
"""

import pyaudio
import wave
import struct
import math
import matplotlib.pyplot as plt
import numpy as np
print("It is Recording.....")
print("If you want to stop just press 'Ctrl + C' ")

CHUNK = 1024
FORMAT = pyaudio.paInt16
SHORT_NORMALIZE = (1.0/32768.0)
CHANNELS = 2
RATE = 44100

def get_rms( block ):
	count = len(block)/2
	format = "%dh"%(count)
	shorts = struct.unpack( format, block )
	sum_squares = 0.0

	for sample in shorts:
		n = sample * SHORT_NORMALIZE
		sum_squares += n*n

	return math.sqrt( sum_squares / count )

p = pyaudio.PyAudio()

plotData = [0] * 100

stream = p.open(format=FORMAT,
                channels=CHANNELS,
                rate=RATE,
                input=True,
                frames_per_buffer=CHUNK)

plt.ion()
try:
	while True:
		data = stream.read(CHUNK)
		plotData.insert(0,get_rms(data))
		plotData.pop()
		x = range(100)
		plt.clf()
		plt.plot(x, plotData)
		plt.draw()
		plt.pause(0.01)
except KeyboardInterrupt:
	pass

plt.show(block=True)
stream.stop_stream()
stream.close()
p.terminate()