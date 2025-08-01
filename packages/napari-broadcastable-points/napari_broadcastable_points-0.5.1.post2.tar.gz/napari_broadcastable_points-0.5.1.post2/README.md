# napari-broadcastable-points

[![License](https://img.shields.io/pypi/l/napari-broadcastable-points.svg?color=green)](https://github.com/ianhi/napari-broadcastable-points/raw/main/LICENSE)
[![PyPI](https://img.shields.io/pypi/v/napari-broadcastable-points.svg?color=green)](https://pypi.org/project/napari-broadcastable-points)
[![Python Version](https://img.shields.io/pypi/pyversions/napari-broadcastable-points.svg?color=green)](https://python.org)

Points layer that can broadcast over arbitrary dimensions. Available here as a workaround until something more complete is implemented in napari core (https://github.com/napari/napari/issues/2343).

**Warning!** This is likely to be very brittle for all the reasons discussed in the napari issue - so while it is useful it should also be used with caution. So don't muck around much with the viewer dims after creating, because who knows what will happen.

### Installation
```bash
pip install napari-broadcastable-points
```


### Usage
Here is an example where we have an  image sequence of (TPCZYX) and we broadcast points over the `C` and `Z` axes.

```python
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

v.dims.axis_labels = ('T', 'P', 'C', 'Z', 'Y', 'X')

points = BroadcastablePoints(dat, broadcast_dims = (2, 3))
v.add_layer(points)
napari.run()
```

![example usage](images/points-broadcasting.gif)


**Creating an empty layer**

You can also create an empty layer - but be sure to specify `ndim` otherwise you may run into an error.

```python
points = BroadcastablePoints(None, broadcast_dims = (2, 3), ndim=6)
```



<!-- [![CI](https://github.com/ianhi/napari-broadcastable-points/actions/workflows/ci/badge.svg)](https://github.com/ianhi/napari-broadcastable-points/actions) -->
<!-- [![codecov](https://codecov.io/gh/ianhi/napari-broadcastable-points/branch/master/graph/badge.svg)](https://codecov.io/gh/ianhi/napari-broadcastable-points) -->
