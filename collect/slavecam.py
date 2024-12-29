from multiprocessing import Pipe, Process
from hardware import init_camera, get_camera
import RPi.GPIO as gpio
import cv2, time, os, signal

# GPIO Pins
CAPTURE_PIN = 21  
END_PIN = 20      

# Parameters
SAVE_DIR = "../data/pusht"
IMG_SIZE = (1024, 1024)  # (width, height) for capture
SAVE_IMG_SIZE = (512, 512)  # Resized dimensions for saving

def init_gpio(capture_pin, end_pin, capture_callback, end_callback):
  gpio.setmode(gpio.BCM)
  gpio.setup(capture_pin, gpio.IN, pull_up_down=gpio.PUD_DOWN)
  gpio.setup(end_pin, gpio.IN, pull_up_down=gpio.PUD_DOWN)

  # Add event detection for capture and end signals
  gpio.add_event_detect(capture_pin, gpio.RISING, callback=capture_callback, bouncetime=50)
  gpio.add_event_detect(end_pin, gpio.RISING, callback=end_callback, bouncetime=50)

# Save Process
def save_images(save_dir, save_img_size, data_con):
  if not os.path.exists(save_dir):
    os.makedirs(save_dir)
  try:
    while True:
      timestamp, img = data_con.recv()
      resized_img = cv2.resize(img, save_img_size, interpolation=cv2.INTER_AREA)
      filename = f"{save_dir}/capture_{timestamp}.png"
      cv2.imwrite(filename, resized_img)
      print(f"Saved image: {filename}")
  except EOFError:  # Pipe closed, exit process
    print("Save process exiting...")
  finally:
    print("Save process cleanup complete.")

# Callback Functions
def capture_callback(channel):
  global camera, data_con_out
  print("Capture signal received!")
  timestamp = time.strftime("%Y%m%d_%H%M%S")
  img = get_camera(camera)
  data_con_out.send((timestamp, img))

def end_callback(channel):
  print("End signal received!")
  raise SystemExit  # Gracefully exit the program

# Main Slave Camera Process
def slavecam():
  global camera, data_con_out

  print("Initializing Slave Camera...")
  init_gpio(CAPTURE_PIN, END_PIN, capture_callback, end_callback)
  camera = init_camera(*IMG_SIZE)
  save_cmd_con_out, save_cmd_con_in = Pipe()
  data_con_out, data_con_in = Pipe()

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
    save_cmd_con_out.close()
    data_con_out.close()
    camera.stop()
    gpio.cleanup()
    save_proc.join()
    print("Slave Camera Shut Down.")

# Entry Point
if __name__ == "__main__":
  slavecam()
