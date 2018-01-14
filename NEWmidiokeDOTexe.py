# -*- coding: utf-8 -*-
"""
Created on a Sunday

@author: Georgios Kyziridis and Geerten Verweij
"""

import pyaudio
import wave
import struct
import math
import matplotlib.pyplot as plt
import numpy as np
from midiutil import MIDIFile
from scipy.signal import fftconvolve
from matplotlib.mlab import find

CHUNK = 4096
FORMAT = pyaudio.paInt16
SHORT_NORMALIZE = (1.0/32768.0)
CHANNELS = 1
RATE = 44100
MIDIout = MIDIFile(1)
MIDIout.addTempo(0, 0, 60)
THRESHOLD = 10

def getRms(block):
	"""
	Standard method to calculate the energy in one chunk
	This code is not made by us
	"""
	count = len(block)/2
	format = "%dh"%(count)
	shorts = struct.unpack( format, block )
	sum_squares = 0.0

	for sample in shorts:
		n = sample * SHORT_NORMALIZE
		sum_squares += n*n

	return math.sqrt( sum_squares / count )

def parabolic(f, x):
	"""
	Quadratic interpolation for estimating the true position of an
	inter-sample maximum which gives us better frequency estimation
	This code is not made by us
	"""
	xv = 1/2. * (f[x-1] - f[x+1]) / (f[x-1] - 2 * f[x] + f[x+1]) + x
	yv = f[x] - 1/4. * (f[x-1] - f[x+1]) * (xv - x)
	return (xv, yv)

def getFrequencies(sig, fs):
	"""
	ready made fundemental frequency detection method that works much better
	than what we tried manually with fft and autocorrelation
	"""
	# Calculate autocorrelation (same thing as convolution, but with
	# one input reversed in time), and throw away the negative lags
	corr = fftconvolve(sig, sig[::-1], mode='full')
	corr = corr[len(corr)//2:]

	# Find the first low point
	d = np.diff(corr)
	start = find(d > 0)[0]

	# Find the next peak after the low point (other than 0 lag).  This bit is
	# not reliable for long signals, due to the desired peak occurring between
	# samples, and other peaks appearing higher.
	# Should use a weighting function to de-emphasize the peaks at longer lags.
	peak = np.argmax(corr[start:]) + start
	px, py = parabolic(corr, peak)

	return fs / px

def freqToMidi(freqValue):
	"""
	convert a frequency in Hertz to a midi pitch
	frequencies are limited between 20 and 4000 Hz to match expected input
	"""
	midiValue = int(round(69+12*math.log(max([(min([freqValue, 4000])), 20])/440,2)))
	return midiValue

p = pyaudio.PyAudio()

plotPitch = [0] * 100
plotEnergy = [0] * 100
plotThreshold = [THRESHOLD] * 100
x = range(100)

stream = p.open(format=FORMAT,
                channels=CHANNELS,
                rate=RATE,
                input=True,
                frames_per_buffer=CHUNK)

plt.ion()

time = 0;

endTime = input("\nProvide how long (in sec) to record: ")

print("It is Recording.....")

while time < int(endTime):
	chunk = stream.read(CHUNK)
	data = np.fromstring(chunk,np.int16)
	freq = getFrequencies(data, RATE)
	pitch = freqToMidi(freq)
	energy = getRms(chunk)* 1000
	plotPitch.insert(0,pitch)
	plotPitch.pop()
	plotEnergy.insert(0,energy)
	plotEnergy.pop()
	if energy > THRESHOLD:
		MIDIout.addNote(0, 0, pitch, time, CHUNK/RATE, 100)
	time = time + (CHUNK/RATE)
	plt.clf()
	plt.plot(x, plotPitch, label='Pitch')
	plt.plot(x, plotEnergy, label='Energy')
	plt.plot(x, plotThreshold, label='Threshold')
	plt.legend()
	plt.draw()
	plt.pause(0.01)


plt.show(block=True)
stream.stop_stream()
stream.close()
p.terminate()

with open("outPut.mid", "wb") as output_file:
    MIDIout.writeFile(output_file)

print("\nMidi is exported as outPut.mid in your file directory")
print("\n                   ||Support MIDIOKE||")