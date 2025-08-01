import napari
import numpy as np
import tifffile

import notochoordinates

img = tifffile.imread("dapt-01.tif")
labels = tifffile.imread("dapt-01_cp_masks.tif")
points = np.array(
    [
        [31.0, 340.83333333, 1013.61929825],
        [35.0, 493.53508772, 859.12105263],
        [36.0, 604.91754386, 706.41929825],
        [37.0, 660.60877193, 573.47894737],
        [38.0, 662.40526316, 392.03333333],
        [40.0, 595.93508772, 264.48245614],
        [41.0, 502.51754386, 163.87894737],
    ]
)

viewer = napari.Viewer()

widget = notochoordinates.Notochoords(viewer)
viewer.window.add_dock_widget(widget)

viewer.add_image(img, channel_axis=1)
viewer.add_labels(labels)
viewer.add_points(points)

widget._fitspline()

viewer.layers.selection.clear()
viewer.layers.selection.add(viewer.layers[2])

widget._cylindrical_coordinates()

viewer.layers.selection.clear()
viewer.layers.selection.add(viewer.layers[5])
viewer.layers.selection.add(viewer.layers[6])
viewer.layers.selection.add(viewer.layers[7])

widget._reslicespline()

napari.run()
