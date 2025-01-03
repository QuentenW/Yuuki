import numpy as np
from ..collect import hardware as hw
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
    servos = hw.init_servos()
    camera = hw.init_camera(*img_size)
    pots = hw.init_pots()
    # set up networking
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    sock.connect((host, port))
    sock.sendall('1'.encode()) # code for master
    sock.recv(bufsize) # be acknowledged
    traj = np.tile([90, 0, 180, 90], Ta).reshape(Ta, 4)# start position
    t = 0
    while True:
      # send info
      img = hw.get_image(camera)
      pos = hw.get_pots(pots)
      tcp.send_buffered_data(sock, img.tobytes())
      tcp.send_buffered_data(sock, np.array(pos).tobytes())
      if t >= To and 0 == t % Ta: # get trajectory
        traj = np.frombuffer(tcp.get_buffered_data(sock))
      hw.set_servos(servos, traj[t % Ta])
      t += 1
  finally:
    sock.close()
    camera.stop()
