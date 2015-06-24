"""
utilities to generate mock (fake) reconstruction inputs for testing purposes.

Example:

.. code-block:: python

    from ctapipe.io import camera
    geom = camera.make_rectangular_camera_geometry()
    showermodel = shower_model(centroid=[0.25, 0.0], 
                               length=0.1,width=0.02, phi=np.radians(40))
    image, signal, noise = make_mock_shower_image(geom, showermodel)
                                            

"""

import numpy as np
from scipy.stats import multivariate_normal

def shower_model(centroid, width, length, phi):
    """
    Create a stastical model (2D gaussian) for a shower image in a
    camera.

    Parameters
    ----------

    centroid: (float,float)
        position of the centroid of the shower in camera coordinates
    width: float
        width of shower (minor axis)
    length: float
        length of shower (major axis)
    phi: float
        rotation angle in radians

    Returns
    -------

    a `scipy.stats` object

    """
    aligned_covariance = np.array([[width, 0], [0, length]])
    # rotate by phi angle: C' = R C R+
    rotation = np.array([[np.cos(phi), -np.sin(phi)],
                         [np.sin(phi),  np.cos(phi)]])
    rotated_covariance = rotation.dot(aligned_covariance).dot(rotation.T)
    return multivariate_normal(mean=centroid, cov=rotated_covariance)


def make_mock_shower_image(geom, showermodel, intensity=50, nsb_level_pe=50):
    """Generates a pedestal-subtracted shower image from a statiscal
    shower model (as generated by `shower_model`). The resulting image
    will be in the same format as the given `CameraGeometry`.

    Parameters
    ----------
    geom: `ctapipe.io.CameraGeometry`
        camera geometry object 
    showermodel: scipy.stats model
        model for the shower to generate in the camera
    intensity: int
        factor to multiply the model by to get photo-electrons
    nsb_level_pe: type
        level of NSB/pedestal in photo-electrons


    Returns
    -------

    an array of image intensities corresponding to the given `CameraGeometry`

    """
    pos = np.empty(geom.pix_x.shape + (2,))
    pos[..., 0] = geom.pix_x.value
    pos[..., 1] = geom.pix_y.value

    model_counts = (showermodel.pdf(pos) * intensity).astype(np.int32)
    signal = np.random.poisson(model_counts)
    noise = np.random.poisson(nsb_level_pe, size=signal.shape)
    image = (signal + noise) - np.mean(noise)

    return image, signal, noise


if __name__ == '__main__':

    from matplotlib import pylab as plt
    from ctapipe.io import camera

    geom = camera.make_rectangular_camera_geometry()

    showermodel = shower_model(centroid=[0.25, 0.0], length=0.1,
                               width=0.02, phi=np.radians(40))

    image, signal, noise = make_mock_shower_image(geom, showermodel,
                                                  intensity=20, nsb_level_pe=30)

    plt.figure(figsize=(10, 3))
    plt.subplot(1, 3, 1)
    plt.imshow(signal, interpolation='none')
    plt.colorbar()
    plt.subplot(1, 3, 2)
    plt.imshow(noise, interpolation='none')
    plt.colorbar()
    plt.subplot(1, 3, 3)
    plt.imshow(image, interpolation='none')
    plt.colorbar()
