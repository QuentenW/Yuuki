from typing import List
from multiprocessing.connection import Connection
import time

import board, busio
from picamera2 import Picamera2
import adafruit_ads1x15.ads1115 as ADS
from adafruit_ads1x15.analog_in import AnalogIn
from adafruit_servokit import ServoKit

import communication as coms


### Notes
# TODO: Set up control class interface
# TODO: Create function to run human control in loop as a process
# TODO: All vector operations are done as lists but numpy might be faster/better, test


#### Magic numbers
dof = 4
servo_bot = [6600, 5700, 6200, 6400]
servo_top = 32767
servo_topdiff = [servo_top - bot for bot in servo_bot]


#### Functions
def human_control_process(
    base_hz:int,
    action_fq:int, # TODO: To update the servos without resampling potentiometer
    save_fq:int,
    pixel_width:int,
    pixel_height:int,
    cmdReceiver:Connection,
    dataCollector:Connection):
  ''''''

  # Setup hardware
  hardware = HardwareInterface(pixel_width, pixel_height)
  n = 0
  while True:
    # Update servo positions
    # TODO: This is just setting the servo to the potentiometer, we want to
    #       use the hardware.propDervControl() to update with a PD-controller
    #       but this will require tuning.
    hardware.updateServo(hardware.get_potentiometer())
    # Send data collector data at save_fq steps
    if n % save_fq == 0:
      dataCollector.send(
        (
          time.time(),
          hardware.get_potentiometer(),
          hardware.get_image()
        )
      )
      n = 0
    # Check if process has been told new command
    if cmdReceiver.poll():
      cmd = cmdReceiver.recv()
      # Break if process is sent termination command
      # NOTE: Can use this to receive different commands
      if cmd == coms.CommandSignal.EXIT:
        break
    # Sleep
    time.sleep(1 / base_hz)
    n += 1

  # Send last data point
  dataCollector.send(
    (
      time.time(),
      hardware.get_potentiometer(),
      hardware.get_image()
    )
  )
  # Clean up steps
  hardware.cleanup()
  cmdReceiver.close()
  dataCollector.close()

def to180(x):
  ''''''
  return round(min(max(x*180, 0), 180))


#### Classes
class HardwareInterface:
  def __init__(
      self,
      pixel_width,
      pixel_height,
      proportion_gain=1,
      derivative_gain=0):
    ''''''

    # Parameters
    self.pixel_width = pixel_width
    self.pixel_height = pixel_height
    #TODO: The PD-controller paramters will need to be tuned
    self.k_p = proportion_gain
    self.k_d = derivative_gain

    # Setup servo
    self.servos = ServoKit(channels=16).servo #NOTE: Should "16" be variable?
    # Setup potentiometers
    self.ads = ADS.ADS1115(busio.I2C(board.SCL, board.SDA))
    self.potentiometer = [
      AnalogIn(self.ads, ADS.P0),
      AnalogIn(self.ads, ADS.P1),
      AnalogIn(self.ads, ADS.P2),
      AnalogIn(self.ads, ADS.P3)
    ]
    self.dof = 4 #NOTE: Degrees of freedom magic number

    # Setup camera
    self.camera = Picamera2()
    self.camera.configure(
      self.camera.create_still_configuration({
        'size': (pixel_width, pixel_height)
      })
    )
    self.camera.start() #NOTE: Maybe start camera separately

    # Setup servo positions
    # TODO: This should maybe (conditionally) reset to some start position
    self.positions = self.get_potentiometer()
    self.velocities = [0 for _ in self.positions]

  def propDervControl(self, action, dt):
    '''Uses proportion-derivative control to update servo positions.'''

    acceleration = [
      self.k_p * (action[i] - self.positions[i]) - self.k_v * self.velocities[i]
      for i in range(self.dof)
    ]
    self.velocities = [acceleration[i]*dt + self.velocities[i] for i in range(self.dof)]
    self.positions = [self.velocities[i]*dt + + self.positions[i] for i in range(self.dof)]

    self.updateServo(self.positions)

  def updateServo(self, position):
    ''''''
    # TODO: Need some safety checks here

    for i in range(3):
      self.servos[i].angle = 180 - to180((position[i] - servo_bot[i]) / servo_topdiff[i])
    self.servos[3].angle = to180((position[3] - servo_bot[3]) / servo_topdiff[i])

  def get_image(self):
    ''''''
    return self.camera.capture_array()

  def get_positions(self):
    return self.positions

  def get_potentiometer(self) -> List[int]:
    '''Returns list of potentiometer values'''
    return [p.value for p in self.potentiometer]

  def cleanup(self):
    '''Clean up hardware setup after use.'''

    self.camera.stop()
    # TODO: Other cleanup?