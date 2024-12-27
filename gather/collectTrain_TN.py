import board, busio, time, json, gc
import adafruit_ads1x15.ads1115 as ADS
from adafruit_ads1x15.analog_in import AnalogIn
from adafruit_servokit import ServoKit
from picamera2 import Picamera2, Preview

import cv2
import time
import json

# Paramters
SAVE_VALUES = True
camera_fps = 10
cam_serv_ratio = 10
servo_fps = camera_fps * cam_serv_ratio
num_servo = 4
pixel_width = 1024
pixel_height = 1024
save_pixel_width = 512
save_pixel_height = 512

# setup servo, pots, camera
servos = ServoKit(channels=16).servo
ads = ADS.ADS1115(busio.I2C(board.SCL, board.SDA))
pots = [AnalogIn(ads, ADS.P0), AnalogIn(ads, ADS.P1),
        AnalogIn(ads, ADS.P2), AnalogIn(ads, ADS.P3)]
c = Picamera2()
c.configure(c.create_still_configuration(
    {'size': (pixel_width, pixel_height)
}))
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
        print(180 - to180((ctrl[i]-bot[i])/(top-bot[i])))
        servos[i].angle = 180 - to180((ctrl[i]-bot[i])/(top-bot[i]))
    servos[3].angle = to180((ctrl[3]-bot[3])/(top-bot[3]))


file_timestamp = time.strftime('%Y%m%d-%H%M%S')
video_writer = cv2.VideoWriter(
    f"data/output_video_{file_timestamp}.mp4",
    cv2.VideoWriter_fourcc(*"mp4v"),  # Codec for MP4
    camera_fps,
    (save_pixel_width, save_pixel_height)
)

positional_data = {}  # Dictionary to store timestamps and positional data
n = 0
try:
    while True:
        if n == cam_serv_ratio and SAVE_VALUES:
            print('Saving position and image')
            # Capture timestamp
            timestamp = time.time()
            new_pos = [p.value for p in pots]
            positional_data[timestamp] = new_pos
            # Get image and resize
            frame = c.capture_array()
            frame_resize = cv2.resize(
                frame,
                (save_pixel_width, save_pixel_height), interpolation=cv2.INTER_AREA
            )
            # Write frame to video file
            video_writer.write(frame_resize)
            # Pause for simulation (adjust interval for actual actuation)
            n = 0
        new_pos = [p.value for p in pots]
        update(servos, new_pos)
        time.sleep(1 / servo_fps)
        n += 1

except KeyboardInterrupt:
    if SAVE_VALUES:
        print('Saving position and image')
        # Capture timestamp
        timestamp = time.time()
        new_pos = [p.value for p in pots]
        positional_data[timestamp] = new_pos
        frame = c.capture_array()
        frame_resize = cv2.resize(
            frame,
            (save_pixel_width, save_pixel_height), interpolation=cv2.INTER_AREA
        )
        # Write frame to video file
        video_writer.write(frame_resize)
        print("Stopping video capture.")

finally:
    if SAVE_VALUES:
        # Save positional data
        with open(f"data/positional_data_{file_timestamp}.json", "w") as f:
            json.dump(positional_data, f, indent=4)

        video_writer.release()
        print("Video capture complete. Positional data saved.")
