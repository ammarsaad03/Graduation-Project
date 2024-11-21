import tkinter as tk
from tkinter import ttk, filedialog, messagebox
from PIL import Image, ImageTk
import os
from hide import HideImage, HideAudio 
from unhide import UnhideImage, UnhideAudio
import cv2
import numpy as np

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

def display_images(original_path, modified_path, display_frame): 
    for widget in display_frame.winfo_children(): 
        widget.destroy() 
    original_image = Image.open(original_path) 
    modified_image = Image.open(modified_path) 
    original_image.thumbnail((300, 300)) 
    modified_image.thumbnail((300, 300)) 
    original_photo = ImageTk.PhotoImage(original_image) 
    modified_photo = ImageTk.PhotoImage(modified_image) 
    
    original_label = ttk.Label(display_frame, text="Original File") 
    original_label.pack(side="top", padx=10, pady=10) 
    original_image_label = ttk.Label(display_frame, image=original_photo) 
    original_image_label.image = original_photo 
    original_image_label.pack(side="top", padx=10, pady=10) 
    
    modified_label = ttk.Label(display_frame, text="Modified File") 
    modified_label.pack(side="top", padx=10, pady=10) 
    modified_image_label = ttk.Label(display_frame, image=modified_photo) 
    modified_image_label.image = modified_photo 
    modified_image_label.pack(side="top", padx=10, pady=10)
    
    display_frame.pack(fill="both", expand=True)
# Function to handle hide action
def hide_action(file_path_var, file_type_var, text_area, display_frame):
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

    try: 
        if file_type == "Image": 
            image_hider = HideImage(file_path, output_path) 
        else: 
            hider = HideAudio(file_path, output_path) 
        image_hider.embed_text_lsb(text_to_hide) 
        messagebox.showinfo("Success", f"Data hidden and saved to {output_path} successfully!") 
        display_images(file_path, output_path, display_frame)
    except Exception as e: 
        messagebox.showerror("Error", f"An error occurred: {str(e)}")
# Function to handle unhide action
def unhide_action(file_path_var, file_type_var, result_box):
    file_path = file_path_var.get()
    file_type = file_type_var.get()

    if not file_path or file_path == "No file uploaded":
        messagebox.showerror("Error", f"Please upload an {file_type} file.")
        return
    try: 
        if file_type == "Image": 
            unhider = UnhideImage(file_path) 
        else: 
            unhider = UnhideAudio(file_path) 
        extracted_text = unhider.extract_text_lsb() 
        result_box.config(state="normal") 
        result_box.delete("1.0", tk.END) 
        result_box.insert("1.0", extracted_text) 
        result_box.config(state="disabled") 
        messagebox.showinfo("Success", f"Data extracted from {file_path}!") 
    except Exception as e: 
        messagebox.showerror("Error", f"An error occurred: {str(e)}")

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
    display_frame = ttk.Frame(frame) 
    
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
            frame, text="Hide Data", command=lambda: hide_action(file_path_var, file_type_var, text_area,display_frame)
        )
        hide_button.pack(pady=10)
        display_frame.pack(fill="both", expand=True)
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
