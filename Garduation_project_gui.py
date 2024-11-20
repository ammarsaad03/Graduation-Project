import tkinter as tk
from tkinter import ttk, filedialog, messagebox
from PIL import Image, ImageTk
import os

import cv2
import numpy as np

def extract_text_lsb(image_path):
    # Load the stego image
    image = cv2.imread(image_path)
    if image is None:
        raise ValueError("Image not found. Check the path.")
    
    # Flatten the image to access all pixels
    flat_image = image.flatten()
    
    # Extract the least significant bits (LSB) from each pixel
    binary_message = ''.join(str(flat_image[i] & 1) for i in range(len(flat_image)))
    
    # Convert binary data to characters until the delimiter (00000000) is found
    chars = [binary_message[i:i+8] for i in range(0, len(binary_message), 8)]
    
    # Stop at the delimiter (00000000) and reconstruct the message
    message = ''
    for char in chars:
        if char == '00000000':  # This is the delimiter, so stop
            break
        message += chr(int(char, 2))  # Convert binary to character
    
    return message
def embed_text_lsb(image_path, output_path, message):
    # Load the image
    image = cv2.imread(image_path)
    if image is None:
        raise ValueError("Image not found. Check the path.")
    
    # Convert the message to binary (8 bits per character)
    binary_message = ''.join(format(ord(char), '08b') for char in message) + '00000000'  # Add delimiter
    message_len = len(binary_message)
    
    # Flatten the image to access all pixels
    flat_image = image.flatten().astype(np.int16)  # Use int16 to handle larger range during processing
    
    if message_len > len(flat_image):
        raise ValueError("Message is too long to fit in the image.")
    
    # Embed the message
    for i in range(message_len):
        # Get the original pixel value
        original_pixel = flat_image[i]
        
        # Clear the LSB (set to 0)
        original_pixel &= ~1  # This clears the LSB
        
        # Ensure the value stays within int16 range before embedding message
        original_pixel = np.clip(original_pixel, -32768, 32767)
        
        # Set the LSB to the message bit
        message_bit = int(binary_message[i])
        modified_pixel = original_pixel | message_bit
        
        # Ensure the modified pixel is within the valid int16 range before clipping
        modified_pixel = np.clip(modified_pixel, -32768, 32767)
        
        # Update the flat_image with the modified pixel
        flat_image[i] = modified_pixel
    
    # After processing, clip to uint8 range (0-255) and reshape the image
    flat_image = np.clip(flat_image, 0, 255).astype(np.uint8)
    stego_image = flat_image.reshape(image.shape)
    
    # Save the stego image
    cv2.imwrite(output_path, stego_image)
    print(f"Message embedded successfully in {output_path}")

# Function to update file format label based on the selected file type
def update_file_format_label(file_type_var, file_path_label, file_path_var, file_format_label):
    file_type = file_type_var.get()
    file_path_label.config(text="No file uploaded")
    file_path_var.set("No file uploaded")
    if file_type == "Image":
        file_format_label.config(text="(*.png;*.jpg;*.jpeg)")
    elif file_type == "Audio":
        file_format_label.config(text="(*.wav;*.mp3)")
    file_format_label.focus_set()


# Function to upload a file
def upload_file(file_type_var, file_path_label, file_path_var):
    file_type = file_type_var.get()
    if file_type == "Image":
        filetypes = [("Image files", "*.png;*.jpg;*.jpeg;*.bmp")]
    elif file_type == "Audio":
        filetypes = [("Audio files", "*.wav;*.mp3")]

    file_path = filedialog.askopenfilename(filetypes=filetypes)
    if file_path:
        file_path_var.set(os.path.abspath(file_path))  # Save the path to the respective variable
        file_path_label.config(text=os.path.abspath(file_path), image="")
    else:
        file_path_var.set("No file uploaded")  # Clear the path if no file is selected


# Function to handle hide action
def hide_action(file_path_var, file_type_var, text_area):
    file_path = file_path_var.get()
    file_type = file_type_var.get()
    print(file_type)
     
    if not file_path or file_path == "No file uploaded":
        messagebox.showerror("Error", f"Please upload an {file_type} file.")
        return

    text_to_hide = text_area.get("1.0", tk.END).strip()
    
    if not text_to_hide:
        messagebox.showerror("Error", "Please enter text to hide.")
        return
    # Ask the user where to save the output file
    output_path = filedialog.asksaveasfilename(
        defaultextension=".png",  # Default file extension
        filetypes=[("Image files", "*.png;*.jpg;*.jpeg;*.bmp")] if file_type == "Image" else [("Audio files", "*.wav")],
        title="Save Stego File"
    )

    if not output_path:
        messagebox.showwarning("Warning", "Save operation cancelled.")
        return

    try:
        if file_type == "Image":
            embed_text_lsb(file_path, output_path, text_to_hide)
        # You can add additional logic for audio here if needed
        messagebox.showinfo("Success", f"Data hidden and saved to {output_path} successfully!")
    except Exception as e:
        messagebox.showerror("Error", f"An error occurred: {str(e)}")

# Function to handle unhide action
def unhide_action(file_path_var, file_type_var, result_box):
    file_path = file_path_var.get()
    file_type = file_type_var.get()

    if not file_path or file_path == "No file uploaded":
        messagebox.showerror("Error", f"Please upload an {file_type} file.")
        return
    extracted_text=""
    try:
        if file_type == "Image":
            extracted_text=extract_text_lsb(file_path)
       
    except Exception as e:
        messagebox.showerror("Error", f"An error occurred: {str(e)}")
    # Your algorithm for extracting hidden data goes here
    #extracted_text = "Sample extracted data"  # Replace with actual extraction logic
    result_box.config(state="normal")
    result_box.delete("1.0", tk.END)
    result_box.insert("1.0", extracted_text)
    result_box.config(state="disabled")
    messagebox.showinfo("Success", f"Data extracted from {file_path}!")


# Function to create a scrollable tab with specific content for hide and unhide
def create_scrollable_tab(notebook, action):
    tab = ttk.Frame(notebook)
    notebook.add(tab, text=f"{action} Data")

    # Frame for scrollable content
    scroll_frame = ttk.Frame(tab)
    scroll_frame.pack(fill="both", expand=True)

    # Canvas for scrolling
    canvas = tk.Canvas(scroll_frame)
    canvas.pack(side="left", fill="both", expand=True)

    # Vertical scrollbar
    v_scrollbar = ttk.Scrollbar(scroll_frame, orient="vertical", command=canvas.yview)
    v_scrollbar.pack(side="right", fill="y")

    # Horizontal scrollbar
    h_scrollbar = ttk.Scrollbar(tab, orient="horizontal", command=canvas.xview)
    h_scrollbar.pack(side="bottom", fill="x")

    canvas.configure(yscrollcommand=v_scrollbar.set, xscrollcommand=h_scrollbar.set)

    # Frame inside canvas
    scrollable_frame = ttk.Frame(canvas)
    scrollable_frame.bind(
        "<Configure>",
        lambda e: canvas.configure(scrollregion=canvas.bbox("all"))
    )
    canvas.create_window((0, 0), window=scrollable_frame, anchor="nw")

    # Add content specific to the action (Hide or Unhide)
    create_content(scrollable_frame, action)
    return tab


# Function to add content to the hide and unhide tabs
def create_content(frame, action):
    file_type_var = tk.StringVar(value="Image")
    file_path_var = tk.StringVar(value="No file uploaded")

    # File type selection
    file_type_frame = ttk.LabelFrame(frame, text="Choose File Type")
    file_type_frame.pack(fill="x", padx=10, pady=5)

    ttk.Radiobutton(file_type_frame, text="Image", variable=file_type_var,
                    command=lambda: update_file_format_label(file_type_var, file_path_label, file_path_var, file_format_label),
                    takefocus=False,
                    value="Image").pack(side="left", padx=5, pady=5)
    ttk.Radiobutton(file_type_frame, text="Audio", variable=file_type_var,
                    command=lambda: update_file_format_label(file_type_var, file_path_label, file_path_var, file_format_label),
                    takefocus=False,
                    value="Audio").pack(side="left", padx=5, pady=5)

    # File upload section
    file_upload_frame = ttk.LabelFrame(frame, text="Upload File")
    file_upload_frame.pack(fill="x", padx=10, pady=5)

    file_path_label = ttk.Label(file_upload_frame, text="No file uploaded", relief="solid",width=40)
    file_path_label.pack(side="left",fill="x", padx=10, pady=10, expand=True)

    upload_button = ttk.Button(
        file_upload_frame,
        text="Upload File",
        command=lambda: upload_file(file_type_var, file_path_label, file_path_var)
    )
    upload_button.pack(side="right", padx=10, pady=10)

    file_format_label = ttk.Label(file_upload_frame, text="(*.png;*.jpg;*.jpeg)", foreground="gray", font=("Arial", 8))
    file_format_label.pack(side="right", padx=5)

    # Text area for entering text to hide (for hide tab)
    if action == "Hide":
        text_area_frame = ttk.LabelFrame(frame, text="Text to Hide")
        text_area_frame.pack(fill="both", expand=True, padx=10, pady=5)

        # Frame for text area and scrollbar
        text_area_container = ttk.Frame(text_area_frame)
        text_area_container.pack(fill="both", expand=True, padx=10, pady=10)

        # Create a Text widget and attach a scrollbar
        text_area = tk.Text(text_area_container, wrap="word", height=8)
        text_area.pack(side="left", fill="both", expand=True)

        text_scrollbar = ttk.Scrollbar(text_area_container, orient="vertical", command=text_area.yview)
        text_scrollbar.pack(side="right", fill="y")

        text_area.configure(yscrollcommand=text_scrollbar.set)
        
        hide_button = ttk.Button(
            frame, text="Hide Data", command=lambda: hide_action(file_path_var, file_type_var, text_area)
        )
        hide_button.pack(pady=10)

    # For unhide tab
    elif action == "Unhide":
        result_box_frame = ttk.LabelFrame(frame, text="Extracted Data")
        result_box_frame.pack(fill="both", expand=True, padx=10, pady=5)

        # Frame for result box and scrollbar
        result_box_container = ttk.Frame(result_box_frame)
        result_box_container.pack(fill="both", expand=True, padx=10, pady=10)

        # Create a Text widget and attach a scrollbar
        result_box = tk.Text(result_box_container, wrap="word", height=8, state="disabled")
        result_box.pack(side="left", fill="both", expand=True)

        result_scrollbar = ttk.Scrollbar(result_box_container, orient="vertical", command=result_box.yview)
        result_scrollbar.pack(side="right", fill="y")

        result_box.configure(yscrollcommand=result_scrollbar.set)
        
        unhide_button = ttk.Button(
            frame, text="Unhide Data", command=lambda: unhide_action(file_path_var, file_type_var, result_box)
        )
        unhide_button.pack(pady=10)


# GUI Setup
root = tk.Tk()
root.title("Steganography Tool")

# Set window size and center the window
window_width = 750
window_height =450
screen_width = root.winfo_screenwidth()
screen_height = root.winfo_screenheight()
x_offset = (screen_width - window_width) // 2
y_offset = (screen_height - window_height) // 2
root.geometry(f"{window_width}x{window_height}+{x_offset}+{y_offset}")
style = ttk.Style()
style.layout("TNotebook.Tab", [
    ('Notebook.tab', {'sticky': 'w', 'children': [
        ('Notebook.padding', {'side': 'top', 'sticky': 'w', 'children': [
            ('Notebook.label', {'side': 'top', 'sticky': ''})
        ]})
    ]})
])

# Optional: Customize tab colors
style.configure("TNotebook.Tab", background="red", padding=(10, 5))
# Notebook for Tabs
notebook = ttk.Notebook(root)
notebook.pack(expand=True, fill="both", padx=10, pady=10)

# Create Tabs
create_scrollable_tab(notebook, "Hide")
create_scrollable_tab(notebook, "Unhide")

root.mainloop()
