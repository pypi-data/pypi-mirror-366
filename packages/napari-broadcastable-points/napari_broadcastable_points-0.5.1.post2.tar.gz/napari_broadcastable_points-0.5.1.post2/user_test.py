import napari
from napari_broadcastable_points import BroadcastablePoints
import numpy as np

v = napari.Viewer()

# create a fake timelapse
T = 5
P = 4
C = 3
Z = 2
Y, X = 512, 512
images = np.zeros([T, P, C, Z, Y, X])
v.add_image(images)

# Add the relevant components of points data
# fmt: off
dat = np.array([
       # T,  P,       Y,              X
       [ 0,  0., 340.25071184, 284.13186557],
       [ 0,  0., 312.66551847, 309.95630191],
       [ 0,  0., 240.76794003, 266.81775485],
       [ 0,  0., 240.47448053, 239.81948049],
       [ 0,  1., 261.60356481, 260.36164576],
       [ 0,  1., 309.43746393, 215.16888217],
       [ 0,  1., 371.06395974, 235.12412843]])
# fmt: on

#                      0    1    2   3    4     5
v.dims.axis_labels = ("T", "P", "C", "Z", "Y", "X")

points = BroadcastablePoints(dat, broadcast_dims=(2, 3))
v.add_layer(points)
napari.run()
