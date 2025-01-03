from multiprocessing import Pipe, Process
from util import hardware
import RPi.GPIO as gpio
import cv2, time, os, signal, pickle, time, json

# gpio pins
img_pin = 16
end_pin = 26

# TODO: these args should be from a config, s.t. can be shared
save_dir = '../data/pusht'
img_size = (1024, 1024) # (w, h)
save_img_size = (512, 512)
camera_fps = 10

# Create a new folder with an iterative name
existing_folders = [f for f in os.listdir(save_dir) if os.path.isdir(os.path.join(save_dir, f))]
new_folder_name = f"save_folder_{len(existing_folders) + 1}"
new_folder_path = os.path.join(save_dir, new_folder_name)
os.makedirs(new_folder_path)
save_id = time.time()

# Update file paths to save in the new folder
video_path = os.path.join(new_folder_path, f"video2_{save_id}.mp4")
json_path = os.path.join(new_folder_path, f"times2_{save_id}.json")

camera = hardware.init_camera(*img_size)
video_writer = cv2.VideoWriter(video_path,
                                cv2.VideoWriter_fourcc(*'mp4v'),
                                camera_fps, save_img_size)
timestamp_data = []
gpio.setmode(gpio.BCM)
gpio.setup(img_pin, gpio.IN, pull_up_down=gpio.PUD_DOWN)
gpio.setup(end_pin, gpio.IN, pull_up_down=gpio.PUD_DOWN)

while True:
  if gpio.input(img_pin)==gpio.HIGH:
    img = hardware.get_image(camera)
    img_resize = cv2.resize(img, save_img_size,
                            interpolation=cv2.INTER_AREA)
    video_writer.write(img_resize)
    timestamp = time.time()
    timestamp_data.append(timestamp)
    print('pulsed')
    time.sleep(0.0015)
  if gpio.input(end_pin)==gpio.HIGH:
    print('end')
    video_writer.release()
    camera.stop()
    gpio.cleanup()
    with open(json_path, 'w') as file:
      json.dump(timestamp_data, file, indent=4)
    break
