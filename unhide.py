import cv2
import numpy as np

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

class UnhideAudio:
    def __init__(self, audio_path):
        self.audio_path = audio_path

    def extract_text_lsb(self):
        # Implement the algorithm for extracting text from audio files
        pass
