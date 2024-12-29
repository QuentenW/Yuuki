import customtkinter as tk
import subprocess
import os
from tkinter import filedialog
import shutil

# Get the base directory dynamically
base_dir = os.path.dirname(os.path.abspath(__file__))
scripts_folder = os.path.join(base_dir, "../TCP_Networking")
received_folder = os.path.join(base_dir, "received_images")
os.makedirs(received_folder, exist_ok=True)  # Ensure it exists
processes = {}

tk.set_appearance_mode("dark")
tk.set_default_color_theme("dark-blue")

# Create the main application window
root = tk.CTk()
root.geometry("500x500")  # Adjusted to fit new elements
root.title("Client-Server Script Runner")

def start_script(script_name):
    script_path = os.path.join(scripts_folder, script_name)
    try:
        # Start the script in a new process
        processes[script_name] = subprocess.Popen(["python", script_path])
        print(f"Started {script_name}")
    except Exception as e:
        print(f"Error starting {script_name}: {e}")

def stop_script(script_name):
    if script_name in processes and processes[script_name]:
        processes[script_name].terminate()
        processes[script_name].wait()
        print(f"Stopped {script_name}")

def select_image():
    # Open file dialog to select an image from the received folder
    image_path = filedialog.askopenfilename(
        initialdir=received_folder,
        title="Select Image",
        filetypes=[("Image Files", "*.jpg;*.png;*.jpeg")],
    )
    if image_path:
        selected_image_label.configure(text=f"Selected: {os.path.basename(image_path)}")
        save_button.configure(state=tk.NORMAL)
        save_button.image_path = image_path  # Store the selected image path

def save_image():
    # Get the custom name and save the image
    custom_name = custom_name_entry.get().strip()
    if not custom_name:
        status_label.configure(text="Error: Enter a custom name.", fg_color="red")
        return

    save_path = os.path.join(received_folder, custom_name + ".jpg")
    try:
        shutil.copy(save_button.image_path, save_path)
        status_label.configure(text=f"Image saved as {custom_name}.jpg", fg_color="green")
    except Exception as e:
        status_label.configure(text=f"Error: {e}", fg_color="red")

# Header label
page_label = tk.CTkLabel(root, text="Client-Server Script Runner", font=("Arial", 18))
page_label.pack(pady=20)

# Buttons to start/stop client and server
button_start_client = tk.CTkButton(root, text="Start Client", command=lambda: start_script("client.py"))
button_start_client.pack(pady=10)

button_stop_client = tk.CTkButton(root, text="Stop Client", command=lambda: stop_script("client.py"))
button_stop_client.pack(pady=10)

button_start_server = tk.CTkButton(root, text="Start Server", command=lambda: start_script("server.py"))
button_start_server.pack(pady=10)

button_stop_server = tk.CTkButton(root, text="Stop Server", command=lambda: stop_script("server.py"))
button_stop_server.pack(pady=10)

# Divider
divider = tk.CTkLabel(root, text="-----------------", font=("Arial", 14))
divider.pack(pady=10)

# Section for saving images
selected_image_label = tk.CTkLabel(root, text="No image selected.", font=("Arial", 14))
selected_image_label.pack(pady=10)

select_button = tk.CTkButton(root, text="Select Image", command=select_image)
select_button.pack(pady=10)

custom_name_label = tk.CTkLabel(root, text="Enter Custom Name (without extension):", font=("Arial", 14))
custom_name_label.pack(pady=10)

custom_name_entry = tk.CTkEntry(root, width=300)
custom_name_entry.pack(pady=10)

save_button = tk.CTkButton(root, text="Save Image", state=tk.DISABLED, command=save_image)
save_button.pack(pady=10)

status_label = tk.CTkLabel(root, text="", font=("Arial", 12))
status_label.pack(pady=20)

root.mainloop()

