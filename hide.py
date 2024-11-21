import cv2
import numpy as np

class HideImage:
    def __init__(self, image_path, output_path):
        self.image_path = image_path
        self.output_path = output_path

    def embed_text_lsb(self, message):
        try:
            image = cv2.imread(self.image_path)
            if image is None:
                raise ValueError("Image not found. Check the path.")
            binary_message = ''.join(format(ord(char), '08b') for char in message) + '00000000'
            message_len = len(binary_message)
            flat_image = image.flatten().astype(np.int16)
            if message_len > len(flat_image):
                raise ValueError("Message is too long to fit in the image.")
            for i in range(message_len):
                original_pixel = flat_image[i]
                original_pixel &= ~1
                original_pixel = np.clip(original_pixel, -32768, 32767)
                message_bit = int(binary_message[i])
                modified_pixel = original_pixel | message_bit
                modified_pixel = np.clip(modified_pixel, -32768, 32767)
                flat_image[i] = modified_pixel
            flat_image = np.clip(flat_image, 0, 255).astype(np.uint8)
            stego_image = flat_image.reshape(image.shape)
            cv2.imwrite(self.output_path, stego_image)
            print(f"Message embedded successfully in {self.output_path}")
        except Exception as e:
            raise ValueError(f"Error embedding text: {e}")

class HideAudio:
    def __init__(self, audio_path, output_path):
        self.audio_path = audio_path
        self.output_path = output_path

    def embed_text_lsb(self, message):
        # Implement the algorithm for hiding text in audio files
        pass
