import customtkinter as tk
import subprocess
import os

# Get the base directory dynamically
base_dir = os.path.dirname(os.path.abspath(__file__))
scripts_folder = os.path.join(base_dir, "../TCP_Networking")
processes = {}

# Set the appearance and theme
tk.set_appearance_mode("dark")  
tk.set_default_color_theme("dark-blue")  

# Create the main application window
root = tk.CTk() 
root.geometry("500x350")
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

root.geometry("400x300")
page_label = tk.CTkLabel(root, text="Client-Server Script Runner", font=("Arial", 18))
page_label.pack(pady=20)

button_start_client = tk.CTkButton(root, text="Start Client", command=lambda: start_script("client.py"))
button_start_client.pack(pady=10)

button_stop_client = tk.CTkButton(root, text="Stop Client", command=lambda: stop_script("client.py"))
button_stop_client.pack(pady=10)

button_start_server = tk.CTkButton(root, text="Start Server", command=lambda: start_script("server.py"))
button_start_server.pack(pady=10)

button_stop_server = tk.CTkButton(root, text="Stop Server", command=lambda: stop_script("server.py"))
button_stop_server.pack(pady=10)

root.mainloop()

