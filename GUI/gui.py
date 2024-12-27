import customtkinter as tk
import subprocess
import os

# Get the base directory dynamically
base_dir = os.path.dirname(os.path.abspath(__file__))
scripts_folder = os.path.join(base_dir, "../TCP_Networking")

# Set the appearance and theme
tk.set_appearance_mode("dark")  
tk.set_default_color_theme("dark-blue")  

# Create the main application window
root = tk.CTk() 
root.geometry("500x350")
root.title("Client-Server Script Runner")

def run_script(script_name):
    script_path = os.path.join(scripts_folder, script_name)
    try:
        subprocess.run(["python", script_path], check=True)
    except Exception as e:
        print(f"Error executing {script_name}: {e}")

# Create a label for the page title
page_label = tk.CTkLabel(root, text="Client-Server Script Runner", font=("Arial", 18))
page_label.pack(pady=20)

# Add buttons to execute client and server scripts
button_client = tk.CTkButton(root, text="Run Client Script", command=lambda: run_script("client.py"))
button_client.pack(pady=10)

button_server = tk.CTkButton(root, text="Run Server Script", command=lambda: run_script("server.py"))
button_server.pack(pady=10)

# Start the Tkinter event loop
root.mainloop()

