import numpy
import numpy as np
import scipy
import splinebox


def fit_spline(annotated_points, voxel_size):
    annotated_points_um = annotated_points * voxel_size
    M = annotated_points_um.shape[0]
    spline = splinebox.Spline(M, splinebox.B3())
    spline.knots = annotated_points_um
    return spline


def compute_initial_vector_for_frame(spline):
    start = spline(0)
    stop = spline(spline.M - 1)
    midpoint = start + (stop - start) / 2
    ts = numpy.linspace(0, spline.M - 1, 100)
    normal = numpy.cross(
        start - midpoint, numpy.mean(spline(ts) - midpoint, axis=0)
    )
    initial_vector = numpy.cross(spline(0, derivative=1), normal)
    return initial_vector


def reslice_along_spline(
    spline, imgs, voxel_size_um, step_size_um=None, half_window_size_um=110
):
    output_pixel_size_um = min(voxel_size_um)
    if step_size_um is None:
        step_size_um = output_pixel_size_um

    total_length_um = spline.arc_length()
    print(f"Spline total length {total_length_um=}")

    arc_length_steps_um = numpy.arange(0, total_length_um, step_size_um)
    print("Computing equal steps for spline...", end="")
    parameters = spline.arc_length_to_parameter(arc_length_steps_um)
    print("done.")

    spline_points_um = spline.eval(parameters)
    initial_vector = compute_initial_vector_for_frame(spline)
    moving_frame_um = spline.moving_frame(
        parameters, method="bishop", initial_vector=initial_vector
    )

    uv_steps_um = np.arange(
        -half_window_size_um,
        half_window_size_um + output_pixel_size_um,
        output_pixel_size_um,
    )
    uu_um, vv_um = numpy.meshgrid(uv_steps_um, uv_steps_um)

    normal_planes_um = np.multiply.outer(
        uu_um, moving_frame_um[:, 2]
    ) + np.multiply.outer(vv_um, moving_frame_um[:, 1])

    # Fix the order of the axes (spline position first, before the normal directions)
    normal_planes_um = np.rollaxis(normal_planes_um, 2, 0)

    # Position normal planes on spline
    normal_planes_um += spline_points_um[:, np.newaxis, np.newaxis]

    resliced_imgs = []
    for img in imgs:
        shape = normal_planes_um.shape
        normal_planes_px = normal_planes_um / voxel_size_um
        vals = scipy.ndimage.map_coordinates(
            img, normal_planes_px.reshape(-1, 3).T, order=1
        )
        resliced_img = vals.reshape(shape[:-1]).astype(float)

        # Mask out pixels outside the volume
        mask = (
            (np.min(normal_planes_px, axis=3) < 0)
            | (normal_planes_px[:, :, :, 0] > img.shape[0] - 1)
            | (normal_planes_px[:, :, :, 1] > img.shape[1] - 1)
            | (normal_planes_px[:, :, :, 2] > img.shape[2] - 1)
        )
        resliced_img[mask] = np.nan

        resliced_imgs.append(resliced_img)
    return resliced_imgs


def convert_to_cylindrical_coordinates(points_um, spline, initial_vector=None):
    radii_um = []
    parameters = []
    arc_lengths_um = []
    angles_deg = []

    for point_um in points_um:
        radius, parameter = spline.distance(point_um, return_t=True)
        arc_length = spline.arc_length(parameter)

        radii_um.append(radius)
        parameters.append(parameter)
        arc_lengths_um.append(arc_length)

    radii_um = np.squeeze(np.array(radii_um))
    arc_lengths_um = np.squeeze(np.array(arc_lengths_um))
    parameters = np.squeeze(numpy.array(parameters))
    sort_indices = numpy.argsort(parameters)

    if initial_vector is None:
        initial_vector = compute_initial_vector_for_frame(spline)

    frame = spline.moving_frame(
        parameters[sort_indices],
        method="bishop",
        initial_vector=initial_vector,
    )
    frame = frame[numpy.argsort(sort_indices)]

    for point_um, parameter, normal in zip(
        points_um, parameters, frame[:, 1], strict=False
    ):

        r_vec = point_um - spline(parameter)
        r_vec /= numpy.linalg.norm(r_vec)
        theta = numpy.arccos(numpy.dot(r_vec, normal))
        angles_deg.append(np.rad2deg(theta))

    angles_deg = np.squeeze(np.array(angles_deg))
    return np.stack([radii_um, angles_deg, arc_lengths_um], axis=-1)
