import board, busio
from picamera2 import Picamera2
import adafruit_ads1x15.ads1115 as ADS
from adafruit_ads1x15.analog_in import AnalogIn
from adafruit_servokit import ServoKit

# servos
servo_bot = [6600, 5700, 6200, 6400]
servo_top = 32767
servo_range = [servo_top - bot for bot in servo_bot]

def init_servos():
  return ServoKit(channels=16).servo

def set_servos(servos, position): # TODO safety checks?
  for i in range(4):
    norm_pos = (position[i] - servo_bot[i])/servo_range[i] # [0,1]
    norm_pos = round(min(max(norm_pos*180, 0), 180))    # [0..180]
    servos[i].angle = norm_pos if i==3 else 180 - norm_pos

# pots
def init_pots():
  ads = ADS.ADS1115(busio.I2C(board.SCL, board.SDA))
  return [AnalogIn(ads, ADS.P0),
          AnalogIn(ads, ADS.P1),
          AnalogIn(ads, ADS.P2),
          AnalogIn(ads, ADS.P3)]

def get_pots(pots):
  return [p.value for p in pots]

# camera
def init_camera(width, height):
  camera = Picamera2()
  config = camera.create_still_configuration({'size': (width, height)})
  camera.configure(config)
  camera.start()
  return camera

def get_image(camera):
  return camera.capture_array()
