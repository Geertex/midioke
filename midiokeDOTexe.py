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
CHANNELS = 2
RATE = 44100

def getFFT(data):
    data=data*np.hamming(len(data))
    fft=np.fft.fft(data)
    fft=np.abs(fft)
    #fft=10*np.log10(fft)
    freq=np.fft.fftfreq(len(fft),1.0/RATE)
    return freq[:int(len(freq)/2)],fft[:int(len(fft)/2)]

p = pyaudio.PyAudio()

plotFreq = [0] * 100
plotEnergy = [0] * 100
x = range(100)

stream = p.open(format=FORMAT,
                channels=CHANNELS,
                rate=RATE,
                input=True,
                frames_per_buffer=CHUNK)

plt.ion()
try:
	while True:
		data = np.fromstring(stream.read(CHUNK),np.int16)
		freq, fft2 = getFFT(data)
		maxEng = 0.0
		maxIdx = 0
		for idx, value in enumerate(fft2):
			if value > maxEng:
				maxEng = value
				maxIdx = idx;
		plotEnergy.insert(0,maxEng)
		plotEnergy.pop()
		plotFreq.insert(0,freq[maxIdx])
		plotFreq.pop()
		plt.clf()
		#plt.plot(x, plotEnergy)
		plt.plot(x, plotFreq)
		plt.draw()
		plt.pause(0.02)
except KeyboardInterrupt:
	pass

plt.show(block=True)
stream.stop_stream()
stream.close()
p.terminate()