# -*- coding: utf-8 -*-
"""
Created on Sun Nov 24 22:52:42 2024

@author: dell
"""

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
    