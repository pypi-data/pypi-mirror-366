import splinebox
import numpy
import napari
import spam.deformation
import spam.DIC
import tifffile

im = tifffile.imread("t0001_Channel 2.tif")

p = 300
N = 1000

spline = splinebox.Spline(5, splinebox.B3())
annotated_points = numpy.genfromtxt("250515_pos5_cropped-t0001_Channel 2.tsv", delimiter='\t', skip_header=1)[:,::-1]
spline.knots = annotated_points

spline_points = spline.eval(numpy.linspace(0, 4, N))
spline_points_tan = spline.eval(numpy.linspace(0, 4, N), derivative=True)
for n in tqdm(range(0, N)): spline_points_tan[n] = spline_points_tan[n] / numpy.linalg.norm(spline_points_tan[n])
spline_moving_frame = spline.moving_frame(numpy.linspace(0, 4, N), method="bishop")

z = numpy.array([1.,0.,0.])

# TODO: Anisotropic pixel size
# nPixZ = 30
# nPixYX = 60

zyxPlaneCoordsOrig = numpy.mgrid[0:1,-p:p+1,-p:p+1].reshape(3, -1).T

imOut = numpy.zeros((N, 1+2*p, 1+2*p), dtype=im.dtype)

for n in tqdm(range(0, N)):
    # tan = spline_points_tan[n]
    # z = numpy.array([1., 0., 0.])
    # 
    # rotationAxis = numpy.cross(tan, z)
    # rotationAngleDeg = numpy.rad2deg(numpy.arccos(numpy.dot(z, tan)))
    # 
    # Phi = spam.deformation.computePhi({'r': -rotationAxis*rotationAngleDeg})
    # 
    # displacements = spam.DIC.applyRegistrationToPoints(
    #     Phi,
    #     [0., 0., 0.],
    #     zyxPlaneCoordsOrig.copy()
    # )[:,0:3,-1]
    # zyxPlaneCoordsDef = zyxPlaneCoordsOrig.copy() + displacements

    zyxPlaneCoordsDef = spline_moving_frame[n][1] * zyxPlaneCoordsOrig[:,1].reshape(-1,1) + spline_moving_frame[n][2] * zyxPlaneCoordsOrig[:,2].reshape(-1,1)

    imPlane = scipy.ndimage.map_coordinates(
        im,
        (zyxPlaneCoordsDef + spline_points[n]).T,
        order=1
    ).reshape(1+2*p, 1+2*p)

    imOut[n] = imPlane

tifffile.imwrite("splineWalk.tif", imOut)
