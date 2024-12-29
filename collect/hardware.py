import board, busio, time, comm
from picamera2 import Picamera2
import adafruit_ads1x15.ads1115 as ADS
from adafruit_ads1x15.analog_in import AnalogIn
from adafruit_servokit import ServoKit
import RPi.GPIO as gpio

# magic numbers
servo_bot = [6600, 5700, 6200, 6400]
servo_top = 32767
servo_range = [servo_top - bot for bot in servo_bot]

# pin configuration
master_pin = 17
end_pin = 20
gpio.setmode(gpio.BCM)
gpio.setup(master_pin, gpio.OUT) # master

# servos
def init_servos():
  return ServoKit(channels=16).servo

def set_servos(servos, position): # TODO safety checks?
  for i in range(3):
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

def human_control_process(control_hz, save_rate,
                          img_size, # (w, h)
                          cmd_con, save_con):
  servos = init_servos()
  pots = init_pots()
  camera = init_camera(*img_size)
  t = 1
  while True:
    # check termination
    if cmd_con.poll() and cmd_con.recv()==comm.EXIT:
      camera.stop()
      cmd_con.close()
      save_con.close()
      gpio(end_pin, gpio.HIGH)
      time.sleep(1)
      gpio.cleanup()
      break
    # update servos
    position = get_pots(pots)
    set_servos(servos, position)
    # save
    if t == save_rate:
      gpio.output(master_pin, gpio.HIGH)
      save_con.send((time.time(), position, get_image(camera))) # todo is this enough delay when sending the signal?
      gpio.output(master_pin, gpio.LOW)
      t = 1
    else: t += 1
    time.sleep(1 / control_hz)
  camera.stop()

# todo unfinished pd control
'''
def propDervControl(self, action, dt):
    #Uses proportion-derivative control to update servo positions.
    acceleration = [
      self.k_p * (action[i] - self.positions[i]) - self.k_v * self.velocities[i]
      for i in range(self.dof)
    ]
    self.velocities = [acceleration[i]*dt + self.velocities[i] for i in range(self.dof)]
    self.positions = [self.velocities[i]*dt + self.positions[i] for i in range(self.dof)]

    self.updateServo(self.positions)'''
