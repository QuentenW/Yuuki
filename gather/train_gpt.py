import board, busio, time, json, gc
import adafruit_ads1x15.ads1115 as ADS
from adafruit_ads1x15.analog_in import AnalogIn
from adafruit_servokit import ServoKit
from picamera2 import Picamera2, Preview

import cv2
import time
import json

# Paramters
fps = 10
num_servo = 4
pixel_width = 512
pixel_height = 512

# setup servo, pots, camera
servos = ServoKit(channels=16).servo
ads = ADS.ADS1115(busio.I2C(board.SCL, board.SDA))
pots = [AnalogIn(ads, ADS.P0), AnalogIn(ads, ADS.P1),
        AnalogIn(ads, ADS.P2), AnalogIn(ads, ADS.P3)]
c = Picamera2()
c.configure(c.create_still_configuration({'size': (pixel_width, pixel_height)}))
c.start()

# base: 6600 - 32767 R0: 90
# shoulder: 5700 - 32767 R1: 0
# elbow: 6200 - 32767 R2: 180
# wrist: 6400 - 32767 R3: 90

def update(servos, ctrl):
	bot = [6600, 5700, 6200, 6400]
	top = 32767
	to180 = lambda x: int(min(max(x*180, 0), 180))
	for i in range(3):
			servos[i].angle = 180 - to180((ctrl[i]-bot[i])/(top-bot[i]))
	servos[3].angle = to180((ctrl[3]-bot[3])/(top-bot[3]))

video_writer = cv2.VideoWriter(
    "output_video.mp4",
    cv2.VideoWriter_fourcc(*"mp4v"),  # Codec for MP4
    fps,
    (pixel_width, pixel_height)
)

positional_data = {}  # Dictionary to store timestamps and positional data
try:
    while True:
        frame = c.capture_array()
        # Capture timestamp
        timestamp = time.time()
        # Simulate positional data (replace with actual robot arm data)
        position = [p.value for p in pots]
        positional_data[timestamp] = position
        update(servos, position)
        # Write frame to video file
        video_writer.write(frame)
        # Pause for simulation (adjust interval for actual actuation)
        time.sleep(1 / fps)

except KeyboardInterrupt:
    print("Stopping video capture.")

finally:
    # Save positional data
    with open("positional_data.json", "w") as f:
        json.dump(positional_data, f, indent=4)

    video_writer.release()
    print("Video capture complete. Positional data saved.")