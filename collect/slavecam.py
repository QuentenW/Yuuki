from multiprocessing import Pipe, Process
from hardware import init_camera, get_image
import RPi.GPIO as gpio
import cv2, time, os, signal, pickle

# gpio pins
img_pin = 21
end_pin = 20
# TODO: these args should be from a config, s.t. can be shared
save_dir = '../data/pusht'
img_size = (1024, 1024) # (w, h)
save_img_size = (512, 512)
camera_fps = 10

def snap(camera):# todo replace callbacks w/ something better
  img = get_image(camera)
  img_resize = cv2.resize(img, save_img_size,
                          interpolation=cv2.INTER_AREA)
  video_writer.write(img_resize)

if __name__ == '__main__':
  camera = init_camera(*img_size)
  img_callback_wrap = lambda _: img_callback(camera, data_con_in)
  init_gpio(img_pin, end_pin, img_callback_wrap, end_callback)
  video_writer = cv2.VideoWriter(f'{save_dir}/video2_{save_id}.mp4',
                                 cv2.VideoWriter_fourcc(*'mp4v'),
                                 camera_fps, save_img_size)
  gpio.setmode(gpio.BCM)
  gpio.setup(img_pin, gpio.IN, pull_up_down=gpio.PUD_DOWN)
  gpio.setup(end_pin, gpio.IN, pull_up_down=gpio.PUD_DOWN)
  gpio.add_event_detect(img_pin, gpio.RISING, lambda _: snap(camera), 50)
  gpio.add_event_detect(end_pin, gpio.RISING, lambda _: 1/0, 50)
  while True:
    try: signal.pause() # wait for gpio events
    finally:
      video_writer.release()
      camera.stop()
      gpio.cleanup()
      break
