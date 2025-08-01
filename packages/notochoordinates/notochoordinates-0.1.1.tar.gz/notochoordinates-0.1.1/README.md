# Notochoordinates

Collaborative Project between EPFL Center for Imaging and TOP lab in SV

## General concept
We use a 3D spline annotated on the notochord to extract image slices travelling down the notochord

## Examples
Spline made with 5 hand-annotated knots
![Spline with 5 knots](spline.jpg)

Spline journey using Bishop coordinate system, resliced
![Animation of walking down the spline](splineWalk.gif)

3D rendering of notochord
![3D rendering](3Drendering.jpg)

## Todo
 - [x] Walk in equal = 1px steps along spline
        1. compute total length: spline.arc_length()
        2. split it into N sections: l = numpy.linspace(0, L, N)
        3. turn those back into parameters (takes a few seconds): t = spline.arc_length_to_parameter(l)

 - [x] Take into account anisotropy
        FA: Work in microns and convert back to pixels just at the interpolation

 - [ ] Impose Z direction instead of bishop?
        Rotate current plane?
        This is subjective but we could easily implement Z-up: https://en.wikipedia.org/wiki/Gram%E2%80%93Schmidt_process
        Other interesting options:
          - Maximise how good a mirror image the reslice is?
          - Point towards the yolk?

 - [ ] Manage extrapolation?
        Going to have to hack a continue-in-same-direction condition

 - [ ] Napari output filename resliced

 - [ ] Detect labels input and turn off interpolation → Reslice selected layer

 - [ ] Capture filename and save annotations and spline
       - Save/Load: annotated points, spline and (nPix, pixel size) to check for application to new images
       - Command-line helper function to reslice images along a saved spline?

 - [ ] Correct annotated point for the spline?

 - [ ] Measuer radial distance from spline and arc length along the spline for each cell using `spline.distance`
