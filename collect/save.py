from multiprocessing.connection import Connection
from select import select
import cv2, json, comm

'''process for saving image frames as mp4 video and corresponding positon data as json'''
def save_process(save_dir, save_id,
                 camera_fps, save_img_size, # (w, h)
                 cmd_con, data_con):
  video_writer = cv2.VideoWriter(f'{save_dir}/video1_{save_id}.mp4',
                                 cv2.VideoWriter_fourcc(*'mp4v'),
                                 camera_fps, save_img_size)
  position_data = {}
  while True:
    # wait for signal from save pipe or command pipe
    cons, _, _ = select([cmd_con, data_con], [], [])
    if data_con in cons: # store image and position data
      timestamp, position, img = data_con.recv()
      position_data[timestamp] = position
      img_resize = cv2.resize(img, save_img_size,
                              interpolation=cv2.INTER_AREA)
      video_writer.write(img_resize)
    if cmd_con in cons and cmd_con.recv()==comm.EXIT: # save and exit
      with open(f'{save_dir}/positions_{save_id}.json', 'w') as file:
        json.dump(position_data, file, indent=4)
      video_writer.release() # save video and close writer
      cmd_con.close()
      data_con.close()
      break
