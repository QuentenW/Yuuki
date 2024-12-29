from multiprocessing import Pipe, Process
from hardware import init_camera, get_image
import RPi.GPIO as gpio
import cv2, time, os, signal, pickle

# GPIO Pins
CAPTURE_PIN = 21
END_PIN = 20

# Parameters
# TODO: save_dir should be an argument from somewhere
SAVE_DIR = "../data/pusht"
IMG_SIZE = (1024, 1024)  # (width, height) for capture
SAVE_IMG_SIZE = (512, 512)  # Resized dimensions for saving
CAMERA_FPS = 10


def init_gpio(capture_pin, end_pin, capture_callback, end_callback):
  gpio.setmode(gpio.BCM)
  gpio.setup(capture_pin, gpio.IN, pull_up_down=gpio.PUD_DOWN)
  gpio.setup(end_pin, gpio.IN, pull_up_down=gpio.PUD_DOWN)

  # Add event detection for capture and end signals
  gpio.add_event_detect(capture_pin, gpio.RISING, callback=capture_callback, bouncetime=50)
  gpio.add_event_detect(end_pin, gpio.RISING, callback=end_callback, bouncetime=50)

# Save Process
def save_images(save_dir, save_id, save_img_size, data_con):
  # Setup video writer and timestamp data structure
  video_writer = cv2.VideoWriter(
    f'{save_dir}/video2_{save_id}.mp4',
    cv2.VideoWriter_fourcc(*'mp4v'),
    CAMERA_FPS, save_img_size
  )
  timestamp_data = []

  if not os.path.exists(save_dir):
    os.makedirs(save_dir)
  try:
    while True:
      timestamp, img = data_con.recv()
      timestamp_data.append(timestamp)
      resized_img = cv2.resize(img, save_img_size, interpolation=cv2.INTER_AREA)
      video_writer.write(resized_img)
  except EOFError:  # Pipe closed, exit process
    print("Save process exiting...")
  finally:
    video_writer.release()
    with open(f'{save_dir}/times2_{save_id}.pkl', 'wb') as file:
      pickle.dump(timestamp_data, file)

    print("Save process cleanup complete.")

# Callback Functions
def capture_callback(channel, camera, data_con_out):
  # global camera, data_con_out
  print("Capture signal received!")
  timestamp = time.strftime("%Y%m%d_%H%M%S")
  img = get_image(camera)
  data_con_out.send((timestamp, img))

def end_callback(channel):
  print("End signal received!")
  raise SystemExit  # Gracefully exit the program

# Main Slave Camera Process
def slavecam():
  # global camera, data_con_out

  # Create img save pipe
  data_con_out, data_con_in = Pipe()
  print("Initializing Slave Camera...")
  camera = init_camera(*IMG_SIZE)
  # Create wrapper
  capture_callback_wrap = lambda channel : capture_callback(
    channel=channel,
    camera=camera,
    data_con_out=data_con_out
  )
  init_gpio(CAPTURE_PIN, END_PIN, capture_callback_wrap, end_callback)

  save_proc = Process(target=save_images, args=(SAVE_DIR, SAVE_IMG_SIZE, data_con_in))
  save_proc.start()

  print("Slave Camera Ready. Waiting for signals...")
  try:
    # Wait for GPIO events
    signal.pause()
  except SystemExit:
    print("Exiting due to end signal...")
  finally:
    print("Cleaning up resources...")
    data_con_out.close()
    save_proc.join()
    camera.stop()
    gpio.cleanup()
    print("Slave Camera Shut Down.")

# Entry Point
if __name__ == "__main__":
  slavecam()
