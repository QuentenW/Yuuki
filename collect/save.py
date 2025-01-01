from multiprocessing.connection import Connection
from select import select
import cv2, json, comm, os

'''process for saving image frames as mp4 video and corresponding positon data as json'''
def save_process(save_dir, save_id, camera_fps, save_img_size, cmd_con, data_con):
  print("sams")
  # Create a new folder with an iterative name
  existing_folders = [f for f in os.listdir(save_dir) if os.path.isdir(os.path.join(save_dir, f))]
  new_folder_name = f"save_folder_{len(existing_folders) + 1}"
  new_folder_path = os.path.join(save_dir, new_folder_name)
  os.makedirs(new_folder_path)

  # Update file paths to save in the new folder
  video_path = os.path.join(new_folder_path, f"video1_{save_id}.mp4")
  json_path = os.path.join(new_folder_path, f"positions_{save_id}.json")

  video_writer = cv2.VideoWriter(video_path, cv2.VideoWriter_fourcc(*'mp4v'), camera_fps, save_img_size)
  position_data = {}

  while True:
    # Wait for signal from save pipe or command pipe
    print('save waits')
    cons, _, _ = select([cmd_con, data_con], [], [])
    if data_con in cons:  # Store image and position data
      timestamp, position, img = data_con.recv()
      position_data[timestamp] = position
      img_resize = cv2.resize(img, save_img_size, interpolation=cv2.INTER_AREA)
      video_writer.write(img_resize)
    if cmd_con in cons and cmd_con.recv() == comm.EXIT:  # Save and exit
      with open(json_path, 'w') as file:
        json.dump(position_data, file, indent=4)
      video_writer.release()  # Save video and close writer
      cmd_con.close()
      data_con.close()
      break
