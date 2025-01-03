import numpy as np
import time, socket, tcp

# parameters
To = 2  # observation horison (table 17)
Ta = 8  # action execution horison (table 17)
# Tp = 16 # action prediction horison (table 17)
img_size = (512, 512)
host = '0.0.0.0' # listen on all interfaces
port = 5000
bufsize = 4096
wait_time = 0.1

if __name__=='__main__':
  try:
    serv_sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    serv_sock.bind((host, port))
    serv_sock.listen()
    slave_con, slave_adr = serv_sock.accept()
    id = int(slave_con.recv(bufsize).decode('utf-8').strip())
    if id: # slave sends 0, master sends 1
      master_con, master_adr = slave_con, slave_adr
      slave_con, slave_adr = serv_sock.accept()
      slave_con.recv(bufsize)
    else:
      master_con, master_adr = serv_sock.accept()
      master_con.recv(bufsize)
    slave_con.sendall(b'ACK_ID')
    master_con.sendall(b'ACK_ID')
    obs = []
    t = 0
    while True:
      # get images + positions
      slave_img = np.frombuffer(tcp.get_buffered_data(slave_con))
      master_img = np.frombuffer(tcp.get_buffered_data(master_con))
      position = np.frombuffer(tcp.get_buffered_data(master_con))
      obs += [(slave_img, master_img, position)]
      if t >= To:
        obs = obs[1:]
        if 0 == t % Ta: # send control
          traj = np.zeros((Ta, 4)) # TODO1 this part calls the ml on <obs>, assumes this is only Ta things
          tcp.send_buffered_data(master_con, traj.tobytes())
      t += 1
      time.sleep(wait_time)
  finally:
    serv_sock.close()
    slave_con.close()
    master_con.close()
