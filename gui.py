import streamlit as st
from hide import HideImage, HideAudio
from unhide import UnhideImage, UnhideAudio
import os
import cv2
import wave

# -------------------------------
# Helpers to calculate max capacity
# -------------------------------
def max_capacity_image(image_path):
    """Calculates the approximate max capacity of an image in bytes."""
    try:
        image = cv2.imread(image_path)
        if image is None:
            return 0
        height, width, channels = image.shape
        # Using Pixel Value Differencing (PVD), capacity is complex.
        # A rough estimate is around 15-20% of the total pixels in bytes.
        # Let's provide a conservative estimate.
        # This is a placeholder; a more accurate PVD capacity function would be complex.
        return (height * width) // 8 # A very rough estimate in bytes
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

# -------------------------------
# Configuration
# -------------------------------
st.set_page_config(page_title="Steganography Assistant", layout="wide")

# -------------------------------
# Title and Branding
# -------------------------------
st.title("🔐 Steganography Assistant")
st.caption("Securely hide and reveal messages in image or audio files using steganography.")

# -------------------------------
# Chat Start
# -------------------------------
with st.chat_message("assistant"):
    st.write("Hi there! 👋 How can I assist you today?")
    process = st.radio("Choose an operation:", ["Hide a Message", "Unhide a Message"], index=None, key="main_op")

# -------------------------------
# Process Handler
# -------------------------------
if process:
    with st.chat_message("user"):
        st.write(f"You selected: **{process}**")

    col1, col2 = st.columns([2, 3])

    if process == "Hide a Message":
        with col1:
            st.subheader("📁 Select Media Type")
            media_type = st.radio("Choose where to hide the message:", ["Image", "Audio"], index=None, key="media_type_hide")

        if media_type == "Image":
            with col1:
                st.subheader("🖼️ Upload an Image File")
                uploaded_img = st.file_uploader("Supported formats: PNG (recommended), JPG", type=["png", "jpg", "jpeg"], key="img_uploader_hide")

            if uploaded_img:
                # Save the uploaded image temporarily to disk for processing
                original_path = "temp_uploaded_image.png"
                with open(original_path, "wb") as f:
                    f.write(uploaded_img.getbuffer())

                with col1:
                    st.image(original_path, caption="Original Image", use_container_width=True)
                    capacity = max_capacity_image(original_path)
                    st.info(f"Estimated capacity: ~{capacity} characters.")

                with col2:
                    st.subheader("✉️ Enter Your Secret Message")
                    message = st.text_area("Type the secret message:", height=150, key="msg_hide_img")

                    if st.button("Hide Message in Image"):
                        if message: # Check if message is not empty
                            output_path = "encoded_image.png"
                            try:
                                stego_img = HideImage(original_path, output_path)
                                stego_img.embed_text_pvd(message) # Assumes PVD method from your lib
                                st.success("✅ Message embedded successfully!")

                                # Show stego image and provide download
                                st.image(output_path, caption="Stego Image (with hidden message)", use_container_width=True)
                                with open(output_path, "rb") as f:
                                    st.download_button("⬇️ Download Encoded Image", f, file_name="stego_image.png")

                            except Exception as e:
                                st.error(f"❌ An error occurred during encoding: {e}")
                                st.warning("The message might be too long for this image. Try a shorter message or a larger image.")
                        else:
                            st.warning("⚠️ Please enter a message to hide.")

        elif media_type == "Audio":
            with col1:
                st.subheader("🎧 Upload an Audio File")
                uploaded_audio = st.file_uploader("Supported formats: WAV (recommended)", type=["wav"], key="audio_uploader_hide")

            if uploaded_audio:
                # Save the uploaded audio temporarily to disk for processing
                original_audio_path = "temp_uploaded_audio.wav"
                with open(original_audio_path, "wb") as f:
                    f.write(uploaded_audio.getbuffer())

                with col1:
                    st.audio(original_audio_path, format="audio/wav")
                    capacity = max_capacity_audio(original_audio_path)
                    st.info(f"File capacity: ~{capacity} characters.")

                with col2:
                    st.subheader("✉️ Enter Your Secret Message")
                    message = st.text_area("Type the secret message:", height=150, key="msg_hide_audio")

                    if st.button("Hide Message in Audio"):
                        if message: # Check if message is not empty
                            output_path = "encoded_audio.wav"
                            try:
                                stego_audio = HideAudio(original_audio_path, output_path)
                                stego_audio.embed_text_lsb(message) # Assumes LSB method from your lib
                                st.success("✅ Message successfully embedded into the audio.")

                                # Show stego audio and provide download
                                st.audio(output_path, format="audio/wav")
                                with open(output_path, "rb") as f:
                                    st.download_button("⬇️ Download Encoded Audio", f, file_name="stego_audio.wav")
                            except Exception as e:
                                st.error(f"❌ An error occurred during encoding: {e}")
                                st.warning("The message might be too long for this audio file. Try a shorter message or a longer audio file.")

                        else:
                            st.warning("⚠️ Please enter a message to hide.")

    elif process == "Unhide a Message":
        with col1:
            st.subheader("📁 Select Media Type")
            media_type = st.radio("Choose file type to extract message from:", ["Image", "Audio"], index=None, key="media_type_unhide")

        if media_type == "Image":
            with col2:
                st.subheader("🖼️ Upload Stego Image File")
                uploaded_img = st.file_uploader("Upload the image containing a hidden message", type=["png", "jpg", "jpeg"], key="img_uploader_unhide")

                if uploaded_img:
                    st.image(uploaded_img, caption="Uploaded Image", use_container_width=True)

                    if st.button("Reveal Message from Image"):
                        try:
                            # UnhideImage needs a file-like object or path
                            # Giving it the uploaded_img object directly is often best
                            extract_img = UnhideImage(uploaded_img)
                            hidden_message = extract_img.extract_text_pvd()

                            with st.chat_message("assistant"):
                                st.subheader("🕵️ Extracted Message")
                                st.code(hidden_message, language=None)
                        except Exception as e:
                            st.error(f"❌ Failed to extract message: {e}")
                            st.info("This could happen if no message is hidden, the file is corrupted, or the wrong method is used.")

        elif media_type == "Audio":
            with col2:
                st.subheader("🎧 Upload Stego Audio File")
                uploaded_audio = st.file_uploader("Upload the audio file containing a hidden message", type=["wav"], key="audio_uploader_unhide")

                if uploaded_audio:
                    st.audio(uploaded_audio)

                    if st.button("Reveal Message from Audio"):
                        try:
                            # UnhideAudio needs a file-like object or path
                            extract_audio = UnhideAudio(uploaded_audio)
                            hidden_message = extract_audio.extract_text_lsb()

                            with st.chat_message("assistant"):
                                st.subheader("🕵️ Extracted Message")
                                st.code(hidden_message, language=None)
                        except Exception as e:
                            st.error(f"❌ Failed to extract message: {e}")
                            st.info("This could happen if no message is hidden, the file is corrupted, or the wrong method is used.")
