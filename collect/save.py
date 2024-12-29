from multiprocessing.connection import Connection
from select import select
import cv2, json, comm

def save_process(
    save_dir, save_id,
    camera_fps, save_img_size, # (w, h)
    cmd_con, data_con):
  '''
  Process for saving image frames as mp4 video and corresponding positon data as json.
  '''

  # Setup video writer and position data structure
  video_writer = cv2.VideoWriter(
    f'{save_dir}/video1_{save_id}.mp4',
    cv2.VideoWriter_fourcc(*'mp4v'),
    camera_fps, save_img_size
  )
  position_data = {}

  while True:
    # Wait for signal from save pipe or command pipe
    cons, _, _ = select([cmd_con, data_con], [], [])
    # Save image and position data
    if data_con in cons:
      # Received data and save with timestamp
      timestamp, position, img = data_con.recv()
      position_data[timestamp] = position
      # Resize image and save
      img_resize = cv2.resize(img, save_img_size, interpolation=cv2.INTER_AREA)
      video_writer.write(img_resize)

    # Check if exit signal has been received and save positions and images
    if cmd_con in cons and cmd_con.recv()==comm.EXIT:
      # Save positions in json
      with open(f'{save_dir}/positions_{save_id}.json', 'w') as file:
        json.dump(position_data, file, indent=4)
      # Save video and close writer
      video_writer.release()
      # Close pipes
      cmd_con.close()
      data_con.close()
      break
