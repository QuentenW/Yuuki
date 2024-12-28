import socket
import os
import threading

# server configuration
HOST = '0.0.0.0'  # listen on all interfaces
PORT = 5000
BUFFER_SIZE = 4096
output_dir = 'received_images'

def handle_connection(conn, addr):
    print(f'Handling connection from {addr}')
    try:
        while True:
            # Receive the original filename (ensure it's text data)
            original_filename = conn.recv(BUFFER_SIZE).decode('utf-8').strip()
            if not original_filename:
                print(f'No filename received or client {addr} disconnected.')
                break
            # Acknowledge receipt of the filename
            conn.sendall(b'ACK_FILENAME')
            # Receive image size (ensure it's text data)
            image_size_data = conn.recv(BUFFER_SIZE).decode('utf-8').strip()
            if not image_size_data:
                print(f"No image size received or client {addr} disconnected.")
                break
            try:
                image_size = int(image_size_data)
            except ValueError:
                print(f"Invalid image size received from {addr}: {image_size_data}")
                break

            conn.sendall(b"ACK_IMAGE_SIZE")  # Acknowledge image size

            # Receive image data (binary data)
            image_data = b""
            while len(image_data) < image_size:
                packet = conn.recv(BUFFER_SIZE)
                if not packet:
                    print(f"Connection interrupted while receiving image data from {addr}.")
                    return
                image_data += packet

            # Save the image with a unique name
            ip, port = addr
            safe_ip = ip.replace('.', '_')  # Replace dots in IP for a valid filename
            prepended_filename = f"{safe_ip}_{port}_{original_filename}"  # Prepend client address
            image_path = os.path.join(output_dir, prepended_filename)
            with open(image_path, "wb") as f:
                f.write(image_data)
            print(f"Image saved to {image_path}")

            # Process the image with ML algorithm (stub for now)
            servo_positions = [45, 90, 135, 180]  # Replace with ML algorithm output

            # Send servo positions
            command = ",".join(map(str, servo_positions))
            conn.sendall(command.encode())
            print(f"Sent servo positions to {addr}: {command}")

    except Exception as e:
        print(f"Error with client {addr}: {e}")
    finally:
        conn.close()
        print(f"Connection with {addr} closed.")

if __name__=='__main__':
    os.makedirs(output_dir, exist_ok=True)
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as server_socket:
        server_socket.bind((HOST, PORT))
        server_socket.listen(5)  # Allow up to 5 queued connections
        print(f"Server listening on {HOST}:{PORT}")

        while True:
            conn, addr = server_socket.accept()
            print(f"Connection from {addr}")
            client_thread = threading.Thread(target=handle_connection, args=(conn, addr))
            client_thread.daemon = True  # Allow thread to exit when the main program ends
            client_thread.start()
