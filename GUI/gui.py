import customtkinter as tk

tk.set_appearance_mode("dark")
tk.set_default_color_theme("dark-blue")

root = tk.CTk()
root.geometry("500x350")

def test():
    print("yes dad")

frame = tk.CTkFrame(master=root)
frame.pack(pady=20, padx=60, fill="both", expand=True)

label = tk.CTkLabel(master=frame, text="Home Page", font=("Roboto", 24))
label.pack(pady=12, padx=10)

# Add buttons to execute different scripts
button1 = tk.CTkButton(master=frame, text="Run Script 1", command=test)
button1.pack(pady=10)

button2 = tk.CTkButton(master=frame, text="Run Script 2", command=test)
button2.pack(pady=10)

button3 = tk.CTkButton(master=frame, text="Run Script 3", command=test)
button3.pack(pady=10)

# Start the Tkinter event loop
root.mainloop()

