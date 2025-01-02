from multiprocessing import Pipe, Process
import numpy as np
from select import select
import socket, comm
# note: trying to not bother with cv2 thing because only a little bit needs to be saved, assuming images are To x size numpy arrays being sent

# port + inet con getting observations and unpacking them [at first try doing both and if it's too slow than make 2 pipes]
# port _ inet con that waits until it has observations up to the end of Ta, predicts, and then sends them

# params
To = 2  # observation horison (table 17)
Ta = 8  # action execution horison (table 17)
Tp = 16 # action prediction horison (table 17)
img_size = (512, 512)

host = '0.0.0.0'  # listen on all interfaces
slave_data_port = 5000
master_data_port = 5001
ctrl_port = 5002
bufsize = 4096

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

def data_process(To, Ta, cmd_con, data_con):
  # todo pass in host and port arguments proper instead of using globvar
  slave_sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
  slave_sock.bind((host, slave_data_port))
  slave_sock.listen(5)
  master_sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
  master_sock.bind((host, master_data_port))
  master_sock.listen(5)
  # send and receive and talk to the ml process
  img = np.zeros((2, *img_size, 3)) # (slave img, mast img)
  obs = [] # list of images of length To
  # todo optimise by writing in place to np array
  t = 0
  while True:
    if 0 == t % Ta:
      data_con.send(obs) # send observation to ml process
    # get images and update observation
    con, addr = slave_sock.accept()
    img[0] = get_img(con, addr)
    con, addr = master_sock.accept()
    pos, img[1] = get_img(con, addr)
    obs = obs[1:] + [(img, pos)]
    if cmd_con.poll() and cmd_con.recv()==comm.EXIT:
      slave_sock.close() ; master_sock.close()
      break

def ml_process(cmd_con, data_con):
  sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
  sock.connect((host, port))
  print(f'Connected to server at {HOST}:{PORT}')
  while True:
    cons, _, _ = select([cmd_con, data_con])
    if data_con in cons:
      obs = data_con.recv()
      # send the data (should be its own function later)
      traj = np.zeros(0) # todo this part calls the ml on <obs>
      bin_traj = traj.tobytes()
      sock.sendall(str(len(bin_traj)).encode()) # send size
      sock.recv(bufsize) # wait for ack
      sock.sendall(bin_traj) # send trajectory
    if cmd_con in cons and cmd_con.recv()==comm.EXIT:
      sock.close()
      break
  
if __name__=='__main__':
  data_con_out, data_con_in = Pipe()
  data_cmd_con_out, data_cmd_con_in = Pipe()
  ml_cmd_con_out, ml_cmd_con_in = Pipe()
  data_proc = Process(target=data_process, args=(To, Ta,
                                                 data_cmd_con_out,
                                                 data_con_in))
  ml_proc = Process(target=ml_process, args=(ml_cmd_con_out,
                                             data_con_out))
  ml_proc.start()
  data_proc.start()
  try:
    while True: time.sleep(0.01) # placeholder for curses or whatever
  finally:
    ml_cmd_con_in.send(comm.EXIT) ; ml_proc.join()
    data_cmd_con_in.send(comm.EXIT) ; data_proc.join()
    [con.close() for con in [data_con_out, data_con_in,
      data_cmd_con_out, data_cmd_con_in, ml_cmd_con_out, ml_cmd_con_in]]
