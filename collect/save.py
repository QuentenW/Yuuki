from multiprocessing.connection import Connection
from select import select
import cv2, json, comm

def save_process(save_dir, save_id,
                 camera_fps, save_img_size, # (w, h)
                 cmd_con, data_con):
  video_writer = cv2.VideoWriter(f'{save_dir}/v{save_id}.mp4',
                                 cv2.VideoWriter_fourcc(*'mp4v'),
                                 camera_fps, save_img_size)
  position_data = {}
  while True:
    cons, _, _ = select([cmd_con, data_con], [], []) # poll
    if data_con in cons: # save data
      timestamp, position, img = data_con.recv()
      position_data[timestamp] = position
      img = cv2.resize(img, save_img_size, interpolation=cv2.INTER_AREA)
      video_writer.write(cv2.resize(img, save_img_size,
                                    interpolation=cv2.INTER_AREA))
    if cmd_con in cons and cmd_con.recv()==comm.EXIT: # quit
      with open(f'{save_dir}/p{save_id}.json', 'w') as f:
        json.dump(position_data, f, indent=4)
      video_writer.release()
      cmd_con.close()
      data_con.close()
      break
