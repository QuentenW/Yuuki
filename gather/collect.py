import curses, time
from datetime import timedelta

from hardwareInterface import HardwareInterface
from dataSaver import DataSaver


# TODO: Make some of these command line arguments or in config file
save_dir = "data/pusht"
SAVE_VALUES = True
camera_fps = 10
cam_serv_ratio = 10
servo_fps = camera_fps * cam_serv_ratio
pixel_width = 1024
pixel_height = 1024
save_pixel_width = 512
save_pixel_height = 512


def main(stdscr):
  ''''''

  # Get timestamp for save file names
  start_timestamp = time.time()
  start = time.process_time()
  # Setup hardware controller
  hardware = HardwareInterface(
    pixel_width,
    pixel_height
  )
  # Setup data saver
  dataSaver = DataSaver(
    save_pixel_width,
    save_pixel_height,
    camera_fps,
    save_dir,
    start_timestamp
  )
  # Setup curses
  curses.cbreak()  # Disable line buffering
  stdscr.keypad(True)  # Enable special key handling
  stdscr.timeout(0)  # Set a timeout for `getch` to avoid blocking
  stdscr.addstr(0,0,"Collecting data, press esc to quit.")

  n = 0
  while True:
    # Update servo positions
    # TODO: This is just setting the servo to the potentiometer, we want to
    #       use the hardware.propDervControl() to update with a PD-controller
    #       but this will require tuning.
    hardware.updateServo(hardware.get_potentiometer())

    if n % cam_serv_ratio == 0:
      # Send position and image data to saver
      timestamp = time.time()
      frame = hardware.get_image()
      positions = hardware.get_potentiometer()
      dataSaver.receiveDataFrame(
        timestamp=timestamp,
        position=positions,
        frame=frame,
      )
      # Reset counter
      n = 0

    # Check if key is pressed
    key = stdscr.getch()
    if key == 27:  # Escape key (ASCII 27) to quit
      break
    # Update timer on display
    # TODO: The time seems to pass slowly
    stdscr.addstr(
      1, 0,
      f"Time elapsed: {str(timedelta(seconds=time.process_time()-start))}"
    )
    stdscr.refresh()
    # Sleep
    time.sleep(1 / servo_fps)
    n += 1

  stdscr.clear()
  stdscr.addstr(0,0,"Done collection, saving data.")
  stdscr.refresh()
  dataSaver.saveData()
  hardware.cleanup()

if __name__ == '__main__':
  # Initialize curses screen
  curses.wrapper(main)
