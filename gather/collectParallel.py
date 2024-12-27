from multiprocessing import Pipe, Process
import time

from hardwareInterface import human_control_process
from dataSaver import dataSaveProcess
from displayInterface import displayProcess
import communication as coms

# TODO: Make some of these command line arguments or in config file
save_dir = "data/pusht"
base_hz = 10
action_steps = 10
camera_steps = 10
servo_steps = 10
servo_fq = base_hz * servo_steps
action_fq = base_hz * action_steps
save_fq = base_hz * camera_steps
pixel_width = 1024
pixel_height = 1024
save_pixel_width = 512
save_pixel_height = 512


def main():
  ''''''

  start_timestamp = time.time()
  # Initilize data pipes
  input_receive, input_send = Pipe()
  hardware_cmd_receive, hardware_cmd_send = Pipe()
  saver_receive, saver_send = Pipe()
  saver_cmd_receive, saver_cmd_send = Pipe()
  # Setup processes for display, hardware, and data saving
  display_process = Process(target=displayProcess, args=(input_send, ))
  hardware_process = Process(target=human_control_process,
    args=(
      base_hz,
      action_fq,
      save_fq,
      pixel_width,
      pixel_height,
      hardware_cmd_receive,
      saver_send
    )
  )
  saver_process = Process(target=dataSaveProcess,
    args=(
      save_pixel_width,
      save_pixel_height,
      save_fq,
      save_dir,
      start_timestamp,
      saver_cmd_receive,
      saver_receive
    )
  )
  # Start proesses
  display_process.start()
  hardware_process.start()
  saver_process.start()

  # Monitoring loop monitoring signals from display
  running = True
  while running:
    # Wait until signal is received from display process
    cmd = input_receive.recv()
    # If exit signal is received, shut down processes
    if cmd == coms.CommandSignal.EXIT:
      hardware_cmd_send.send(coms.CommandSignal.EXIT)
      hardware_process.join()
      saver_cmd_send.send(coms.CommandSignal.EXIT)
      saver_process.join()
    else:
      # A problem?
      continue

  display_process.join()


if __name__ == '__main__':
  pass
