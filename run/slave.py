import numpy as np
import ..collect.hardware as hw
import socket, tcp

# parameters
To = 2
Ta = 8
img_size = (512, 512)
host = '0.0.0.0'  # listen on all interfaces
port = 5000
bufsize = 4096

if __name__=='__main__':
  try:
    # set up hardware
    camera = hw.init_camera(*img_size)
    # set up networking
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    sock.connect((host, port))
    sock.sendall('0'.encode()) # code for slave
    sock.recv(bufsize) # be acknowledged
    traj = np.tile([90, 0, 180, 90], Ta).reshape(Ta, 4)# start position
    while True:
      img = hw.get_image(camera)
      tcp.send_buffered_data(sock, img.tobytes())
  finally:
    sock.close()
    camera.stop()
