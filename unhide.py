import wave
import cv2
from PIL import Image
import numpy as np
from operations import  bin_to_str, get_capacity

class UnhideImage:
    def __init__(self, image_path):
        self.image_path = image_path
    
    def extract_text_lsb(self):
        try:
            image = cv2.imread(self.image_path)
            if image is None:
                raise ValueError("Image not found. Check the path.")
            flat_image = image.flatten()
            binary_message = ''.join(str(flat_image[i] & 1) for i in range(len(flat_image)))
            chars = [binary_message[i:i+8] for i in range(0, len(binary_message), 8)]
            message = ''
            for char in chars:
                if char == '00000000':
                    break
                message += chr(int(char, 2))
            return message
        except Exception as e:
            raise ValueError(f"Error extracting text: {e}")
    
    def extract_text_pvd(self):
        # Load the stego image
        stego_image = Image.open(self.image_path)
        pixels = np.array(stego_image, dtype=np.int32)
    
        # Determine image dimensions
        if len(pixels.shape) == 2:  # Grayscale image
            rows, cols = pixels.shape
            channels = 1
        else:  # Color image
            rows, cols, channels = pixels.shape
    
        binary_message = ''
    
        # First extract 32 bits for length prefix
        length_bits_collected = 0
        message_length = None  # in bits
    
        for channel in range(channels):
            channel_data = pixels if channels == 1 else pixels[:, :, channel]
    
            for row in range(rows):
                for col in range(0, cols - 1, 2):
                    p1 = channel_data[row, col]
                    p2 = channel_data[row, col + 1]
                    diff = abs(p1 - p2)
                    bit_capacity = get_capacity(diff)
                    embedded_bits = format(diff, f'0{bit_capacity}b')
    
                    if message_length is None:
                        # Collect length prefix first
                        needed = 32 - length_bits_collected
                        if bit_capacity <= needed:
                            length_bits_collected += bit_capacity
                            length_prefix_part = embedded_bits
                            binary_message += length_prefix_part
                        else:
                            # Split bits between length prefix and message
                            length_prefix_part = embedded_bits[:needed]
                            binary_message += length_prefix_part
                            message_length = int(binary_message, 2)
                            # Start collecting message bits from remainder
                            message_bits_part = embedded_bits[needed:]
                            binary_message = ''  # Reset for message bits
                            binary_message += message_bits_part
                            length_bits_collected = 32
                            continue  # continue embedding message bits
                        if length_bits_collected == 32:
                            message_length = int(binary_message, 2)
                            binary_message = ''
                    else:
                        binary_message += embedded_bits
    
                    # Stop if message bits collected equal length
                    if message_length is not None and len(binary_message) >= message_length:
                        binary_message = binary_message[:message_length]
                        extracted_message = bin_to_str(binary_message)
                        return extracted_message
    
        # If the loop finishes without return, decode whatever collected
        if message_length is not None:
            binary_message = binary_message[:message_length]
            return bin_to_str(binary_message)
        else:
            return ''  # No message found

class UnhideAudio:
    def __init__(self, audio_path):
        self.audio_path = audio_path

    def bits_to_text(self, bits):
        chars = [bits[i:i+8] for i in range(0, len(bits), 8)]
        text = ''.join(chr(int(char, 2)) for char in chars if char != '00000000')
        return text

    def extract_text_lsb(self):
        try:
            with wave.open(self.audio_path, 'rb') as audio:
                frame_bytes = bytearray(list(audio.readframes(audio.getnframes())))

                extracted_bits = []
                for byte in frame_bytes:
                    extracted_bits.append(str(byte & 1))
                    # Check for delimiter in chunks of 8 bits
                    if ''.join(extracted_bits[-8:]) == '00000000':
                        break

                # Convert the extracted bits back to text
                message = self.bits_to_text(''.join(extracted_bits))
            return message
        except Exception as e:
            raise ValueError(f"Error extracting text: {e}")