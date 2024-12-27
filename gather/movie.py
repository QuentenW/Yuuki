import matplotlib.pyplot as plt
import matplotlib.cm as cm
import matplotlib.animation as animation
import numpy as np

raw_data = np.load('data/pusht_20241222-191721.npy')
img_data = raw_data[:,:-4]
imgs = img_data.reshape(50,256,256,3)
print(imgs.shape)

frames = [] # for storing the generated images
fig = plt.figure()
for im in imgs:
    frames.append([plt.imshow(im, cmap=cm.Greys_r,animated=True)])

ani = animation.ArtistAnimation(fig, frames, interval=50, blit=True,
                                repeat_delay=1000)
# ani.save('movie.mp4')
plt.show()