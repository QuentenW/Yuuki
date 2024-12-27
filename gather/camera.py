from picamera2 import Picamera2, Preview

c = Picamera2()
c.configure(c.create_still_configuration({'size': (512, 512)}))
c.start()

a = c.capture_array()
print(a.shape, type(a[0,0,0]))
c.capture_file('test.png')
c.stop()
