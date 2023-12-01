# macOS M1, required these steps for portaudio:
# https://stackoverflow.com/a/73166852
import pyaudio
import numpy as np
from math import sqrt, log
import time
import pygame

pygame.init()
p = pyaudio.PyAudio()

# Get the number of channels that the selected device supports
"""numDevices = p.get_device_count()
for device_index in range(0,numDevices):
    device_name = p.get_device_info_by_index(device_index)
    device_channels = p.get_device_info_by_host_api_device_index(0, device_index).get('maxInputChannels')
    print('Input device %s has %s channels' % (device_name["name"], device_channels))"""

default_device = p.get_default_input_device_info()
print(default_device)

RATE = int(default_device["defaultSampleRate"])
CHUNK = int((1/30) * RATE)
FORMAT = pyaudio.paInt16

stream = p.open(format=FORMAT,
    channels=1,
    rate=RATE,
    input=True,
    input_device_index=default_device["index"],
    frames_per_buffer=CHUNK)

print("***Monitoring")

SCREEN_HEIGHT = 320
screen = pygame.display.set_mode((CHUNK/2, SCREEN_HEIGHT))

done = False
while not done:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            done = True
            break
    start = time.time()
    buff = stream.read(CHUNK, exception_on_overflow = False)
    data = np.frombuffer(buff, dtype=np.int16)
    fft_complex = np.fft.fft(data, n=CHUNK)
    N = int(len(fft_complex)/2)
    fft_complex = fft_complex[1:N]
    screen.fill((0,0,0))
    color = (0,200,104)
    s = 0
    max_val = sqrt(max(v.real * v.real + v.imag * v.imag for v in fft_complex))
    scale_value = 4*SCREEN_HEIGHT # / max_val
    for i,v in enumerate(fft_complex):
        #v = complex(v.real / dist1, v.imag / dist1)
        dist = sqrt(v.real * v.real + v.imag * v.imag)
        mapped_dist = dist/scale_value
        s += mapped_dist
    
        pygame.draw.line(screen, color, (i, SCREEN_HEIGHT), (i, SCREEN_HEIGHT - mapped_dist))
    pygame.display.flip()
    end = time.time()