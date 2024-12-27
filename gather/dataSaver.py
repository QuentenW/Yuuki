from multiprocessing.connection import Connection
import select
import cv2, json

import communication as coms


#### Functions
def dataSaveProcess(
    save_pixel_width:int,
    save_pixel_height:int,
    camera_fps:int,
    save_dir:str,
    start_timestamp:int,
    cmdSender:Connection,
    dataSender:Connection):
  ''''''

  datasaver = DataSaver(
    save_pixel_width,
    save_pixel_height,
    camera_fps,
    save_dir,
    start_timestamp
  )

  running = True
  while running:
    # Wait to receive data or command signal
    received, _, _ = select([cmdSender, dataSender], [], [])
    # Process received
    for rec in received:
      # Give received data to data saver
      if rec is dataSender:
        timestamp, position, imgFrame = dataSender.recv()
        datasaver.receiveDataFrame(
          timestamp=timestamp,
          position=position,
          frame=imgFrame
        )
      # Exit if received exit signal
      elif rec is cmdSender:
        cmd = cmdSender.recv()
        if cmd == coms.CommandSignal.EXIT:
          running = False
      else:
        # Huh??
        continue

  # Cleanup
  datasaver.saveData()
  cmdSender.close()
  dataSender.close()


#### Classes
class DataSaver:
  def __init__(
        self,
        save_pixel_width,
        save_pixel_height,
        camera_fps,
        save_dir,
        start_timestamp):

      # Parameters
      self.save_pixel_width = save_pixel_width
      self.save_pixel_height = save_pixel_height
      self.camera_fps = camera_fps
      self.save_dir = save_dir
      self.time_stamp = start_timestamp

      # Video writer setup
      self.video_writer = cv2.VideoWriter(
        f"{self.save_dir}/video_{self.time_stamp}.mp4",
        cv2.VideoWriter_fourcc(*"mp4v"),  # Codec for MP4
        camera_fps,
        (save_pixel_width, save_pixel_height)
      )
      # Position data
      self.position_data = {}

  def receiveDataFrame(self, timestamp, position, frame):
      ''''''

      # Save position data
      self.spositional_data[timestamp] = position
      # Save video frame
      frame_resize = cv2.resize(
        frame,
        (self.save_pixel_width, self.save_pixel_height),
        interpolation=cv2.INTER_AREA
      )
      # Write frame to video file
      self.video_writer.write(frame_resize)

  def saveData(self):
    ''''''

    # Save position data
    with open(f"{self.save_dir}/position_{self.time_stamp}.json", "w") as f:
      json.dump(self.positional_data, f, indent=4)
    # Save video
    self.video_writer.release()