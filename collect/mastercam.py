import RPi.GPIO as gpio
import time
from picamera2 import Picamera2

# TODO: this stuff should be part of hardware, and when an image is taken it should just be a pulse sending added to that file
# gpio init
pin = 17  # master
gpio.setmode(gpio.BCM)
gpio.setup(pin, gpio.OUT)
# camera init
camera = Picamera2()
camera.configure(camera.create_still_configuration())
camera.start()

def send_pulse_and_capture():
  gpio.output(pin, gpio.HIGH)
  time.sleep(0.1)
  print(gpio.input(pin))
  gpio.output(pin, gpio.LOW)
  print("Pulse sent!")
  timestamp = time.strftime("%Y%m%d_%H%M%S")
  path = f"master_capture_{timestamp}.png"
  camera.capture_file(path)
  print(f"Master image captured: {path}")

try:
  while True:
    pin_state = gpio.input(pin)
    input("Press Enter to capture a synchronized photo...")
    send_pulse_and_capture()
    time.sleep(1)  # delay before the next capture
except KeyboardInterrupt:
  print("Exiting...")
finally:
  camera.stop()
  gpio.cleanup()
