import numpy as np
import socket



host = '0.0.0.0'  # listen on all interfaces
slave_data_port = 5000
master_data_port = 5001
ctrl_port = 5002
bufsize = 4096


with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as sock:
  sock.connect((host, master_data_port))
  img = [] # todo1 take image 
  sock.sendall
def get_img(con, addr, slave=True):
  try:
    # receive image size (int)
    img_size = con.recv(bufsize).decode('utf-8').strip()
    if not img_size:
      print(f'No image size received from {addr}.')
      1/0
    try:
      img_size = int(img_size)
    except ValueError:
      print(f'Invalid image size received from {addr}: {img_size}')
      1/0
    con.sendall(b'ACK_IMAGE_SIZE')
    # receive image (binary data)
    img_data = b''
    while len(img_data) < img_size:
      packet = con.recv(bufsize)
      if not packet: 1/0 # TODO throw an exception
      # print(f'Connection interrupted while receiving \
      #         image data from {addr}.')
      img_data += packet
    if slave:
      con.close()
      return np.frombuffer(img_data)
    # otherwise master, send position data too
    pos_size = con.recv(bufsize).decode('utf-8').strip()
    if not pos_size:
      print(f'No position size received from {addr}.')
      1/0
    try:
      pos_size = int(pos_size)
    except ValueError:
      print(f'Invalid image size received from {addr}: {pos_size}')
      1/0
    con.sendall(b'ACK_POS_SIZE')
    # receive position
    pos_data = b''
    while len(pos_data) < pos_size:
      packet = con.recv(bufsize)
      if not packet: 1/0 # TODO throw an exception
      pos_data += packet
    con.close()
    return pos_data, img_data
  except Exception as e:
    print(f'Error transferring image data from client {addr}: {e}')
    con.close()
