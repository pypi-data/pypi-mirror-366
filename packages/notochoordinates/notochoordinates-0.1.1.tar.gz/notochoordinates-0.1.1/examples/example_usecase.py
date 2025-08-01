import napari
import numpy
import numpy as np
import skimage
import splinebox
import tifffile

import notochoordinates

img = tifffile.imread("dapt-01.tif")
labels = tifffile.imread("dapt-01_cp_masks.tif")
# Load the spline saved with the plugin
spline = splinebox.Spline.from_json("dapt-01-spline.json")

voxel_size_um = np.array([0.7, 0.347, 0.347])

region_props = skimage.measure.regionprops_table(
    labels,
    properties=("label", "centroid", "coords"),
)

centroids_px = numpy.stack(
    [
        region_props["centroid-0"],
        region_props["centroid-1"],
        region_props["centroid-2"],
    ],
    axis=-1,
)
centroids_um = centroids_px * voxel_size_um

# Returns the radius, angle and arc length along the spline for each point in that order
cylindrical_coords = notochoordinates.convert_to_cylindrical_coordinates(
    centroids_um, spline
)

# Reslice channel 0 and 1
resliced_img = notochoordinates.reslice_along_spline(
    spline,
    [img[:, 0], img[:, 1]],
    voxel_size_um,
)

viewer = napari.Viewer()
viewer.add_image(resliced_img[0])
viewer.add_image(resliced_img[1])
napari.run()
