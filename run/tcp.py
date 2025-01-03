import socket

bufsize = 4096

def get_buffered_data(con):
  size = int(con.recv(bufsize).decode('utf-8').strip())
  con.sendall(b'ACK_SIZE')
  data = b''
  while len(data) < size:
    packet = con.recv(bufsize)
    data += packet
  con.sendall(b'ACK_DATA')
  return data

def send_buffered_data(con, data): # assumes data is bytes
  con.sendall(str(len(data)).encode())
  con.recv(bufsize) # ACK_SIZE
  con.sendall(data)
  con.recv(bufsize) # ACK_DATA
