# -*- coding: utf-8 -*-
"""
Created on Sun Nov 24 22:52:42 2024

@author: dell
"""
import cv2
import wave
import os
import numpy as np


def str_to_bin(text):
    return ''.join([format(ord(char), '08b') for char in text])

# Convert binary to string
def bin_to_str(binary_message):
    message = ''.join([chr(int(binary_message[i:i+8], 2)) for i in range(0, len(binary_message), 8)])
    return message

# Function to calculate embedding capacity based on pixel difference
def get_capacity(diff):
    if diff < 16:
        return 1
    elif diff < 32:
        return 2
    elif diff < 64:
        return 3
    elif diff < 128:
        return 4
    else:
        return 5
def max_capacity_image(image_path):
    """Calculates the approximate max capacity of an image in bytes."""
    try:
        image = cv2.imread(image_path)
        if image is None:
            return 0
        height, width, channels = image.shape
        return (height * width) // 8 
    except Exception:
        return 0

def max_capacity_audio(audio_path):
    """Calculates the max capacity of a WAV audio file in bytes for LSB."""
    try:
        with wave.open(audio_path, 'rb') as audio:
            n_frames = audio.getnframes()
            # 1 bit per frame, so n_frames / 8 bytes.
            return n_frames // 8
    except Exception:
        return 0



def plot_waveform(audio_path, title, ax):
    """Reads a WAV file and plots its waveform on a given Matplotlib axis."""
    try:
        with wave.open(audio_path, 'rb') as wf:
            n_frames = wf.getnframes()
            framerate = wf.getframerate()
            signal_wave = wf.readframes(n_frames)
            
            # Determine the data type based on sample width
            sampwidth = wf.getsampwidth()
            if sampwidth == 1:
                dtype = np.uint8 # 8-bit unsigned
            elif sampwidth == 2:
                dtype = np.int16 # 16-bit signed (most common)
            else:
                dtype = np.int32 # 24/32-bit signed
            
            signal_array = np.frombuffer(signal_wave, dtype=dtype)
            
            # Create time axis
            time_axis = np.linspace(0, n_frames / framerate, num=n_frames)
            
            ax.plot(time_axis, signal_array)
            ax.set_title(title, fontsize=10)
            ax.set_xlabel("Time (s)")
            ax.set_ylabel("Amplitude")
            ax.grid(True)
    except Exception as e:
        ax.text(0.5, 0.5, f"Could not plot: {e}", ha='center')
