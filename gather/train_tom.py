import board, busio, time, json, gc
import adafruit_ads1x15.ads1115 as ADS
from adafruit_ads1x15.analog_in import AnalogIn
from adafruit_servokit import ServoKit
from picamera2 import Picamera2, Preview
import numpy as np
import datetime

# setup servo, pots, camera
servos = ServoKit(channels=16).servo
ads = ADS.ADS1115(busio.I2C(board.SCL, board.SDA))
pots = [AnalogIn(ads, ADS.P0), AnalogIn(ads, ADS.P1),
        AnalogIn(ads, ADS.P2), AnalogIn(ads, ADS.P3)]
c = Picamera2()
pixel_width = 256
pixel_height = 256
c.configure(c.create_still_configuration({'size': (pixel_width, pixel_height)}))
c.start()

# base: 6600 - 32767 R0: 90
# shoulder: 5700 - 32767 R1: 0
# elbow: 6200 - 32767 R2: 180
# wrist: 6400 - 32767 R3: 90

num_servo = 4
def update(servos, ctrl):
	bot = [6600, 5700, 6200, 6400]
	top = 32767
	to180 = lambda x: int(min(max(x*180, 0), 180))
	for i in range(3):
			servos[i].angle = 180 - to180((ctrl[i]-bot[i])/(top-bot[i]))
	servos[3].angle = to180((ctrl[3]-bot[3])/(top-bot[3]))

save_rate = 50
data = np.zeros((save_rate, pixel_height, pixel_width, 3), dtype=np.int)
n = 0
try:
	while True:
		ctrl = [p.value for p in pots]
		update(servos, ctrl)
		foo = c.capture_array()

		data[n] = foo
		n += 1
		if n == save_rate:
			# with open('data', mode='a') as f:
			print('start')
			np.save(f'data_{datetime.datetime.now()}.npy', data)
			print('end')
			# data = np.zeros((save_rate, 3*pixel_height*pixel_width + num_servo))
			n = 0
		time.sleep(.1)
except KeyboardInterrupt:
	c.stop()
	print('bye')