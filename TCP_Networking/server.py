import socket
import ssl
import os

# Python TCP server connection for recieving image data and transmitting positional data to a robotic arm
#12/22/2024 Quenten Welch

# Server Configuration
HOST = '0.0.0.0'  # Listen on for IP on all interfaces
PORT = 5000  # Port for communication, selected arbitrarily but must match on client and server
BUFFER_SIZE = 4096
output_dir = "received_images" #directory to store image data
os.makedirs(output_dir, exist_ok=True) 

context = ssl.create_default_context(ssl.Purpose.CLIENT_AUTH)
context.load_cert_chain(certfile="server.crt", keyfile="server.key")

def handle_connection(conn):
    try:
        while True:
            # Receive image size
            image_size_data = conn.recv(BUFFER_SIZE).decode()
            if not image_size_data.strip():  # Check for empty or invalid data
                print("No image size received or client disconnected.")
                break

            try:
                image_size = int(image_size_data)
            except ValueError:
                print(f"Invalid image size received: {image_size_data}")
                break

            conn.sendall(b"ACK")  # Acknowledge

            # Receive image data
            image_data = b""
            while len(image_data) < image_size:
                packet = conn.recv(BUFFER_SIZE)
                if not packet:
                    print("Connection interrupted while receiving image data.")
                    return
                image_data += packet

            # Save the image
            image_path = os.path.join(output_dir, "received_image.jpg")
            with open(image_path, "wb") as f:
                f.write(image_data)
            print(f"Image saved to {image_path}")

            # Process the image with ML algorithm (stub for now)
            servo_positions = [45, 90, 135, 180]  # Replace with ML algorithm output

            # Send servo positions
            command = ",".join(map(str, servo_positions))
            conn.sendall(command.encode())
            print(f"Sent servo positions: {command}")

    except Exception as e:
        print(f"Error: {e}")
    finally:
        conn.close()

# Main Server Loop
with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as server_socket:
    server_socket.bind((HOST, PORT))
    server_socket.listen(1)
    print(f"Server listening on {HOST}:{PORT}")
    with context.wrap_socket(server_socket, server_side=True) as secure_socket:
        conn, addr = secure_socket.accept()
        print(f"Connection from {addr}")
        handle_connection(conn)
