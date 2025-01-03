import time
from util import hardware, comm
import RPi.GPIO as gpio

# parameters
master_pin = 17
end_pin = 16


def human_control_process(control_hz, save_rate,
                          img_size, # (w, h)
                          cmd_con, save_con):
  servos = hardware.init_servos()
  pots = hardware.init_pots()
  camera = hardware.init_camera(*img_size)
  gpio.setmode(gpio.BCM)
  gpio.setup(master_pin, gpio.OUT)
  gpio.setup(end_pin, gpio.OUT)
  t = 1
  while True:
    # check termination
    if cmd_con.poll() and cmd_con.recv()==comm.EXIT:
      camera.stop()
      gpio.output(end_pin, gpio.HIGH)
      time.sleep(1)
      gpio.output(end_pin, gpio.LOW)
      gpio.cleanup()
      break
    # update servos
    position = hardware.get_pots(pots)
    hardware.set_servos(servos, position)
    # save
    if t == save_rate:
      gpio.output(master_pin, gpio.HIGH)
      time.sleep(0.001)
      gpio.output(master_pin, gpio.LOW)
      save_con.send((time.time(), position, hardware.get_image(camera)))
      t = 1
    else: t += 1
    time.sleep(1 / control_hz)


'''# todo unfinished pd control
def propDervControl(self, action, dt):
    #Uses proportion-derivative control to update servo positions.
    acceleration = [self.k_p * (action[i] - self.positions[i])
                    - self.k_v * self.velocities[i]
                    for i in range(self.dof)]
    self.velocities = [acceleration[i]*dt + self.velocities[i] for i in range(self.dof)]
    self.positions = [self.velocities[i]*dt + self.positions[i] for i in range(self.dof)]
    self.updateServo(self.positions)'''
