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
from midiutil import MIDIFile
from scipy.signal import fftconvolve
from matplotlib.mlab import find
print("It is Recording.....")
print("If you want to stop just press 'Ctrl + C' ")

CHUNK = 4096
FORMAT = pyaudio.paInt16
SHORT_NORMALIZE = (1.0/32768.0)
CHANNELS = 1
RATE = 44100
MIDIout = MIDIFile(1)
MIDIout.addTempo(0, 0, 60)

def get_rms( block ):
	count = len(block)/2
	format = "%dh"%(count)
	shorts = struct.unpack( format, block )
	sum_squares = 0.0

	for sample in shorts:
		n = sample * SHORT_NORMALIZE
		sum_squares += n*n

	return math.sqrt( sum_squares / count )

def parabolic(f, x):
	"""Quadratic interpolation for estimating the true position of an
	inter-sample maximum when nearby samples are known.

	f is a vector and x is an index for that vector.

	Returns (vx, vy), the coordinates of the vertex of a parabola that goes
	through point x and its two neighbors.

	Example:
	Defining a vector f with a local maximum at index 3 (= 6), find local
	maximum if points 2, 3, and 4 actually defined a parabola.

	In [3]: f = [2, 3, 1, 6, 4, 2, 3, 1]

	In [4]: parabolic(f, argmax(f))
	Out[4]: (3.2142857142857144, 6.1607142857142856)

	"""
	xv = 1/2. * (f[x-1] - f[x+1]) / (f[x-1] - 2 * f[x] + f[x+1]) + x
	yv = f[x] - 1/4. * (f[x-1] - f[x+1]) * (xv - x)
	return (xv, yv)

def freq_from_autocorr(sig, fs):
	"""
	Estimate frequency using autocorrelation
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
	midiValue = int(round(69+12*math.log(max([(min([freqValue, 4000])), 20])/440,2)))
	return midiValue

p = pyaudio.PyAudio()

plotPitch = [0] * 100
plotEnergy = [0] * 100
x = range(100)

stream = p.open(format=FORMAT,
                channels=CHANNELS,
                rate=RATE,
                input=True,
                frames_per_buffer=CHUNK)

plt.ion()

time = 0;


while time < 20:
	chunk = stream.read(CHUNK)
	data = np.fromstring(chunk,np.int16)
	pitch = freqToMidi(freq_from_autocorr(data, RATE))
	energy = get_rms(chunk)* 1000
	plotPitch.insert(0,pitch)
	plotPitch.pop()
	plotEnergy.insert(0,energy)
	plotEnergy.pop()
	if energy > 10:
		MIDIout.addNote(0, 0, pitch, time, CHUNK/RATE, 100)
	time = time + (CHUNK/RATE)
	plt.clf()
	plt.plot(x, plotPitch)
	plt.plot(x, plotEnergy)
	plt.draw()
	plt.pause(0.01)


plt.show(block=True)
stream.stop_stream()
stream.close()
p.terminate()

with open("politically_correct_expression.mid", "wb") as output_file:
    MIDIout.writeFile(output_file)