from enum import Flag, auto
from multiprocessing.connection import Connection
import select
import time
import cv2, json


#### Data
# NOTE: Add more signal types here for controlling hardware process
class CommandSignal(Flag):
  EXIT = auto()

#### Functions
def receiveFrame(
    frame,
    save_pixel_width:int,
    save_pixel_height:int,
    video_writer:cv2.VideoWriter):
  ''''''

  # Save video frame
  frame_resize = cv2.resize(
    frame,
    (save_pixel_width, save_pixel_height),
    interpolation=cv2.INTER_AREA
  )
  # Write frame to video file
  video_writer.write(frame_resize)

def dataSaveProcess(
    save_pixel_width:int,
    save_pixel_height:int,
    camera_fps:int,
    save_dir:str,
    start_timestamp:int,
    cmdSender:Connection,
    dataSender:Connection):
  ''''''
  # Video writer setup
  video_writer = cv2.VideoWriter(
    f"{save_dir}/video_{start_timestamp}.mp4",
    cv2.VideoWriter_fourcc(*"mp4v"),  # Codec for MP4
    camera_fps,
    (save_pixel_width, save_pixel_height)
  )
  # Position data
  position_data = {}

  running = True
  while running:
    # Wait to receive data or command signal
    received, _, _ = select([cmdSender, dataSender], [], [])
    # Process received
    for rec in received:
      # Give received data to data saver
      if rec is dataSender:
        timestamp, position, imgFrame = dataSender.recv()
        receiveFrame(
          imgFrame,
          save_pixel_width,
          save_pixel_height,
          video_writer
        )
        position_data[timestamp] = position

      # Exit if received exit signal
      elif rec is cmdSender:
        cmd = cmdSender.recv()
        if cmd == CommandSignal.EXIT:
          running = False
      else:
        # Huh??
        continue

  # Save position data
  with open(f"{save_dir}/position_{start_timestamp}.json", "w") as f:
    json.dump(position_data, f, indent=4)
  # Save video
  video_writer.release()
  # Cleanup
  cmdSender.close()
  dataSender.close()