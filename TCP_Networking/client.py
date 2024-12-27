import socket
import os
import time


# Python TCP server connection for sending image data and recieving positional data to a robotic arm
#12/22/2024 Quenten Welch

# Server Configuration
HOST = '10.0.0.166'
PORT = 5000
BUFFER_SIZE = 4096

# Directory containing existing images for testing
image_dir = "test_images"
image_files = os.listdir(image_dir)

if not image_files:
    print(f"No images found in directory: {image_dir}")
    exit()

# Connect to Server
try:
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as client_socket:
        client_socket.connect((HOST, PORT))
        print(f"Connected to server at {HOST}:{PORT}")

        for image_file in image_files:
            # Full path to the image file
            image_path = os.path.join(image_dir, image_file)

            # Ensure it's a file
            if not os.path.isfile(image_path):
                continue

            # Send image size
            image_size = os.path.getsize(image_path)
            client_socket.sendall(str(image_size).encode())
            client_socket.recv(BUFFER_SIZE)  # Wait for ACK

            # Send image data
            with open(image_path, "rb") as f:
                client_socket.sendall(f.read())
            print(f"Image '{image_file}' sent successfully!")

            # Receive servo positions
            data = client_socket.recv(BUFFER_SIZE).decode()
            servo_positions = list(map(int, data.split(",")))
            print(f"Received servo positions: {servo_positions}")

            # Wait a bit before sending the next image
            time.sleep(1)

        client_socket.close()

except Exception as e:
    print(f"Error: {e}")
