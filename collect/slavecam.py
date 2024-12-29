from multiprocessing import Pipe, Process
from hardware import init_camera, get_camera
import RPi.GPIO as gpio
import time, signal, save


# params (image sizes are (w, h) in px)
pin = 21
save_dir = "../data/pusht"
camera_fps = 100/10 # clean this up
img_size = (1024, 1024)
save_img_size = (512, 512)

def init_gpio(pin):
  gpio.setmode(gpio.BCM)
  gpio.setup(pin, gpio.IN, pull_up_down=gpio.PUD_DOWN)

def capture_image():
  timestamp = time.strftime("%Y%m%d_%H%M%S")
  path = f"capture_{timestamp}.png"
  camera.capture_file(path)
  print(f"Image captured: {path}")

def callback(_):
  print("Pulse detected!")
  # todo this should use the camera to send the save process an image
  # todo I'm imitating https://raspberrypi.stackexchange.com/questions/120662/what-is-the-best-way-to-wait-for-gpio-events with the callback syntax, but I think it would be better to just use signal.pause() to wait until an edge detection and have this code run after in the while True loop.
  img = get_camera()

if __name__=="__main__":
  # todo this time.time() is a placeholder, there's no way to get the filenames to match b/w here and master w/o sending data over a con
  # I don't know if a separate process is needed for hardware on this one, but we could to match the style of the other code
  save_id = time.time()
  save_cmd_con_in, save_cmd_con_out = Pipe()
  data_con_in, data_con_out = Pipe()
  save_proc = Process(target=save.save_process,
                      args=(save_dir, save_id,
                            camera_fps, save_img_size,
                            save_cmd_con_in, data_con_in))# todo won't work, expects positions, should just get image in
  gpio.add_event_detect(pin, gpio.RISING,
                        callback=callback, bouncetime=50)
  init_camera(*img_size)
  init_gpio(pin)
  save_proc.start()
  try:
    print("Waiting for synchronization pulse...")
    while True:
      signal.pause()
  except KeyboardInterrupt:# TODO replace with end signal on another pin which would be passed from master
    print("Exiting...")
  finally:
    camera.stop()
    gpio.cleanup()
