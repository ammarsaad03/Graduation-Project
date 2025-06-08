import wave
import cv2
from PIL import Image
import numpy as np
from operations import str_to_bin, get_capacity

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
        except Exception as e:
            raise ValueError(f"Error embedding text: {e}") 

    def get_stego_image(self):
        # Return the stego image as a PIL Image object
        return Image.open(self.output_path)

    # Function to encode a message into an image using PVD
    def embed_text_pvd(self, secret_message):
        # Load the image
        image = Image.open(self.image_path)
        pixels = np.array(image, dtype=np.int32)
    
        binary_msg = str_to_bin(secret_message)
        length_prefix = format(len(binary_msg), '032b')
        binary_message = length_prefix + binary_msg

        binary_index = 0
    
        # Determine image dimensions
        if len(pixels.shape) == 2:  # Grayscale image
            rows, cols = pixels.shape
            channels = 1
        else:  # Color image
            rows, cols, channels = pixels.shape
    
        for channel in range(channels):
            channel_data = pixels if channels == 1 else pixels[:, :, channel]
    
            for row in range(rows):
                for col in range(0, cols - 1, 2):
                    if binary_index >= len(binary_message):
                        break
    
                    # Get the pixel pair
                    p1 = channel_data[row, col]
                    p2 = channel_data[row, col + 1]
    
                    # Calculate the difference between pixel values
                    diff = abs(p1 - p2)
    
                    # Determine embedding capacity
                    bit_capacity = get_capacity(diff)
    
                    # Extract bits to embed
                    bits_to_embed = binary_message[binary_index:binary_index + bit_capacity]
                    if not bits_to_embed:
                        break
                    binary_index += bit_capacity
    
                    # Embed the bits into the pixel pair
                    value_to_embed = int(bits_to_embed, 2)
    
                    if p1 > p2:
                        p2 = max(0, p1 - value_to_embed)
                    else:
                        p1 = max(0, p2 - value_to_embed)
    
                    # Clip pixel values to the valid range [0, 255]
                    p1 = min(255, max(0, p1))
                    p2 = min(255, max(0, p2))
    
                    # Update pixel pair
                    channel_data[row, col], channel_data[row, col + 1] = p1, p2
    
            # Save the updated channel back
            if channels > 1:
                pixels[:, :, channel] = channel_data
    
        # Convert pixel values back to uint8 for image creation
        pixels = np.uint8(np.clip(pixels, 0, 255))
    
        # Save the stego image
        stego_image = Image.fromarray(pixels)
        stego_image.save(self.output_path)

    # New method to calculate max letters that can be hidden using PVD
    def calculate_max_letters_pvd(self):
        image = Image.open(self.image_path)
        pixels = np.array(image, dtype=np.int32)

        if len(pixels.shape) == 2:  # Grayscale image
            rows, cols = pixels.shape
            channels = 1
        else:
            rows, cols, channels = pixels.shape

        total_bits = 0

        for channel in range(channels):
            channel_data = pixels if channels == 1 else pixels[:, :, channel]

            for row in range(rows):
                for col in range(0, cols - 1, 2):
                    p1 = channel_data[row, col]
                    p2 = channel_data[row, col + 1]
                    diff = abs(p1 - p2)
                    total_bits += get_capacity(diff)

        max_letters = total_bits // 8  # 8 bits per letter
        return max_letters


class HideAudio:
    def __init__(self, audio_path, output_path):
        self.audio_path = audio_path
        self.output_path = output_path

    def text_to_bits(self, text):
        return ''.join(format(ord(char), '08b') for char in text) + '00000000'

    def embed_text_lsb(self, message):
        try:
            with wave.open(self.audio_path, 'rb') as audio:
                params = audio.getparams()
                frame_bytes = bytearray(list(audio.readframes(audio.getnframes())))

                message_bits = self.text_to_bits(message)

                if len(message_bits) > len(frame_bytes):
                    raise ValueError("Message too long to encode in this audio file.")

                for i in range(len(message_bits)):
                    frame_bytes[i] = (frame_bytes[i] & 254) | int(message_bits[i])

                with wave.open(self.output_path, 'wb') as encoded_audio:
                    encoded_audio.setparams(params)
                    encoded_audio.writeframes(bytes(frame_bytes))
            print(f"Message encoded and saved as {self.output_path}")
        except Exception as e:
            raise ValueError(f"Error embedding text: {e}")
