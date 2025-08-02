"""
Top-level package for Medial Axis Transform 3D.
@author: Giovanni Bocchi
@mail: giovanni.bocchi1@unimi.it
@institution: University of Milan
"""
# medialaxis3d/__init__.py

__app_name__ = "medialaxis3d"
__version__ = "1.0.2"

(
    SUCCESS,
	MISSING_AGRUMENTS,
) = range(2)

ERRORS = {
    MISSING_AGRUMENTS: "missing arguments error",
}

import numpy as np
from scipy import ndimage as ndi
from importlib.resources import files

from medialaxis3d.skeletonize_cy import _skeletonize_loop, _table_lookup_index, _pattern_of

def _table_lookup(image, table):
    """
    Perform a morphological transform on an image, directed by its
    neighbors

    Parameters
    ----------
    image : ndarray
        A binary image
    table : ndarray
        A 3**3-element table giving the transform of each pixel given
        the values of that pixel and its 27-connected neighbors.

    Returns
    -------
    result : ndarray of same shape as `image`
        Transformed image

    Notes
    -----
    The pixels are numbered like this::

      0 1 2
      3 4 5
      6 7 8

      2**9   2**10  2**11
      2**12  2**13  2**14
      2**15  2**16  2**17

     ...

    The index at a pixel is the sum of 2**<pixel-number> for pixels
    that evaluate to true.
    """

    #
    # We accumulate into the indexer to get the index into the table
    # at each point in the image
    #
    if image.shape[0] < 3 or image.shape[1] < 3 or image.shape[2] < 3:
        image = image.astype(bool)
        indexer = np.zeros(image.shape, int)
        indexer[1:, 1:] += image[:-1, :-1] * 2**0
        indexer[1:, :] += image[:-1, :] * 2**1
        indexer[1:, :-1] += image[:-1, 1:] * 2**2

        indexer[:, 1:] += image[:, :-1] * 2**3
        indexer[:, :] += image[:, :] * 2**4
        indexer[:, :-1] += image[:, 1:] * 2**5

        indexer[:-1, 1:] += image[1:, :-1] * 2**6
        indexer[:-1, :] += image[1:, :] * 2**7
        indexer[:-1, :-1] += image[1:, 1:] * 2**8
    else:
        indexer = _table_lookup_index(np.ascontiguousarray(image, np.uint8))
    image = table[indexer]
    return image

def medial_axis_3d(image, mask = None, return_distance = False, connectivity = 27, lessthantwo = True, size = None, *, rng = None):
    """Compute the medial axis transform of a binary 3D image.

    Parameters
    ----------
    image : binary ndarray, shape (M, N, T)
        The image of the shape to skeletonize. If this input isn't already a
        binary image, it gets converted into one: In this case, zero values are
        considered background (False), nonzero values are considered
        foreground (True).
    mask : binary ndarray, shape (M, N, T), optional
        If a mask is given, only those elements in `image` with a true
        value in `mask` are used for computing the medial axis.
    return_distance : bool, optional
        If true, the distance transform is returned as well as the skeleton.
    connectivity: int, default 27
        The type of connectivity used to skeletonize voxels: can be
        27 (full), 19 (excluding the 8 corners) and 7 (only voxels having an
        adjacent face with the central one).
    lessthantwo: bool, default True
        If True the lookup table will keep voxels having two or less neighbors.
    size: int, optional
        If not None, a mean filter with kernel of sahpe (size, size, size)
        is applied to the distance array before skeletonization.
    rng : {`numpy.random.Generator`, int}, optional
        Pseudo-random number generator.
        By default, a PCG64 generator is used (see :func:`numpy.random.default_rng`).
        If `rng` is an int, it is used to seed the generator.

        The PRNG determines the order in which pixels are processed for
        tiebreaking.

    Returns
    -------
    result : ndarray of bools
        Medial axis transform of the image
    dist : ndarray of floats, optional
        Distance transform of the image (only returned if `return_distance`
        is True)

    Notes
    -----
    This algorithm computes the medial axis transform of an image
    as the ridges of its distance transform.

    The different steps of the algorithm are as follows
     * A lookup table is used, that assigns 0 or 1 to each configuration of
       the 3x3x3 binary cube, whether the central voxel should be removed
       or kept. We want a point to be removed if it has more than one neighbor
       and if removing it does not change the number of connected components.

     * The distance transform to the background is computed, as well as
       the cornerness of the voxel.

     * The foreground (value of 1) points are ordered by
       the distance transform, then the cornerness.

     * A cython function is called to reduce the image to its skeleton. It
       processes voxel in the order determined at the previous step, and
       removes or maintains a voxel according to the lookup table. Because
       of the ordering, it is possible to process all voxels in only one
       pass.

    """
    global _eight_connect
    if mask is None:
        masked_image = image.astype(bool).copy()
    else:
        masked_image = image.astype(bool).copy()
        masked_image[~mask] = False

    # Build lookup table - three conditions
    # 1. Keep only positive voxels (center_is_foreground array).
    # AND
    # 2. Keep if removing the voxel results in a different connectivity
    # (if the number of connected components is different with and
    # without the central voxel)
    # OR
    # 3. Keep if # voxels in neighborhood is 2 or less
    # Note that table is independent of image and indeed it is precomputed

    luts = np.load(files('medialaxis3d.luts').joinpath("luts.npz"))
    foreground = luts['foreground']
    euler27 = luts['euler27']
    euler19 = luts['euler19']
    euler7  = luts['euler7']
    lessthan2 = luts['lessthan2']
    cornerness_table = luts['corners']

    connections = {27: euler27,
                   19: euler19,
                   7:  euler7}

    assert connectivity in [27, 19, 7], "Connectivity should be 27, 19 or 7."

    if lessthantwo:
        table = (foreground & connections[connectivity]) | lessthan2
    else:
        table = (foreground & connections[connectivity])

    # Build distance transform
    distance = ndi.distance_transform_edt(masked_image)
    if size is not None:
        distancec = ndi.correlate(distance,
                                  np.ones((size, size, size)),
                                  mode = "constant") * (distance > 0)
    else:
        distancec = distance

    if return_distance:
        dist = distance.copy()

    # Corners
    # The processing order along the edge is critical to the shape of the
    # resulting skeleton: if you process a corner first, that corner will
    # be eroded and the skeleton will miss the arm from that corner. Pixels
    # with fewer neighbors are more "cornery" and should be processed last.
    # We use a cornerness_table lookup table where the score of a
    # configuration is the number of background (0-value) pixels in the
    # 3x3x3 neighborhood

    corner_score = _table_lookup(masked_image, cornerness_table)

    # Define arrays for inner loop
    i, j, k = np.mgrid[0 : image.shape[0], 0 : image.shape[1], 0 : image.shape[2]]

    masked_image[distance == 1] = False
    result = masked_image.copy()

    # distancel = distance[result]
    distancel = distancec[result]
    i = np.ascontiguousarray(i[result], dtype=np.intp)
    j = np.ascontiguousarray(j[result], dtype=np.intp)
    k = np.ascontiguousarray(k[result], dtype=np.intp)

    result = np.ascontiguousarray(result, np.uint8)

    # Determine the order in which pixels are processed.
    # We use a random # for tiebreaking. Assign each pixel in the image a
    # predictable, random # so that masking doesn't affect arbitrary choices
    # of skeletons

    generator = np.random.default_rng(rng)
    tiebreaker = generator.permutation(np.arange(masked_image.sum()))
    order = np.lexsort((tiebreaker, -corner_score[masked_image], distancel))
    order = np.ascontiguousarray(order, dtype=np.int32)
    table = np.ascontiguousarray(table, dtype=np.uint8)

    # Remove pixels not belonging to the medial axis
    _skeletonize_loop(result, i, j, k, order, table)
    result = result.astype(bool)

    if mask is not None:
        result[~mask] = image[~mask]
    if return_distance:
        return result, dist
    else:
        return result



