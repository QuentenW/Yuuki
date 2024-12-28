import RPi.GPIO as gpio
import time
from picamera2 import Picamera2

# gpio init
pin = 21
gpio.setmode(gpio.BCM)
gpio.setup(pin, gpio.IN, pull_up_down=gpio.PUD_DOWN)
# camera init
camera = Picamera2()
camera.configure(camera.create_still_configuration())
camera.start()

def capture_image():
    timestamp = time.strftime("%Y%m%d_%H%M%S")
    path = f"capture_{timestamp}.png"
    camera.capture_file(path)
    print(f"Image captured: {path}")

if __name__=="__main__":
    try:
        print("Waiting for synchronization pulse...")
        while True:
            if gpio.input(pin)==gpio.HIGH:
                print("Pulse detected!")
                capture_image()
            time.sleep(0.05)  # Debounce to avoid multiple triggers
    except KeyboardInterrupt:
        print("Exiting...")
    finally:
        camera.stop()
        gpio.cleanup()
