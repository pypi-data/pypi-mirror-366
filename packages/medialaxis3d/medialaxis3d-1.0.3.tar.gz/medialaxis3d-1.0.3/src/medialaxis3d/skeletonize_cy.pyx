#cython: language_level=3
#cython: cdivision=True
#cython: boundscheck=False
#cython: nonecheck=False
#cython: wraparound=False

import numpy as np
cimport numpy as cnp
cnp.import_array()

def _pattern_of(Py_ssize_t index):
    """
    Return the pattern represented by an index value
    Byte decomposition of index
    """
    return np.array([[[index & 2**0, index & 2**1, index & 2**2],
                      [index & 2**3, index & 2**4, index & 2**5],
                      [index & 2**6, index & 2**7, index & 2**8]],
                     [[index & 2**9, index & 2**10, index & 2**11],
                      [index & 2**12, index & 2**13, index & 2**14],
                      [index & 2**15, index & 2**16, index & 2**17]],
                     [[index & 2**18, index & 2**19, index & 2**20],
                      [index & 2**21, index & 2**22, index & 2**23],
                      [index & 2**24, index & 2**25, index & 2**26]]],
        bool,
    )
    
def _skeletonize_loop(cnp.uint8_t[:, :, ::1] result,
                      Py_ssize_t[::1] i, Py_ssize_t[::1] j, Py_ssize_t[::1] k,
                      cnp.int32_t[::1] order, cnp.uint8_t[::1] table):
    """
    Inner loop of skeletonize function

    Parameters
    ----------

    result : ndarray of uint8
        On input, the image to be skeletonized, on output the skeletonized
        image.

    i, j, k : ndarrays
        The coordinates of each foreground voxel in the image

    order : ndarray
        The index of each voxel, in the order of processing (order[0] is
        the first voxel to process, etc.)

    table : ndarray
        The 3**3-element lookup table of values after transformation
        (whether to keep or not each configuration in a binary 3x3x3 array)

    Notes
    -----

    The loop determines whether each voxel in the image can be removed without
    changing the Euler number of the image. The voxels are ordered by
    increasing distance from the background which means a point nearer to
    the quench-line of the brushfire will be evaluated later than a
    point closer to the edge.

    Note that the neighborhood of a voxel may evolve before the loop
    arrives at this voxel. This is why it is possible to compute the
    skeleton in only one pass, thanks to an adapted ordering of the
    voxels.
    """
    cdef:
        Py_ssize_t accumulator
        Py_ssize_t index, order_index
        Py_ssize_t ii, jj, kk
        Py_ssize_t rows = result.shape[0]
        Py_ssize_t cols = result.shape[1]
        Py_ssize_t stacks = result.shape[2]

    with nogil:
        for index in range(order.shape[0]):
            accumulator = 2**13
            order_index = order[index]
            ii = i[order_index]
            jj = j[order_index]
            kk = k[order_index]
            
            # Compute the configuration around the voxel
            if ii > 0:
                if jj > 0:
                    if kk > 0:
                        if result[ii-1, jj-1, kk-1]: accumulator += 2**0
                    if result[ii-1, jj-1, kk]: accumulator += 2**1
                    if kk < stacks - 1:
                        if result[ii-1, jj-1, kk+1]: accumulator += 2**2
                if kk > 0:
                    if result[ii-1, jj, kk-1]: accumulator += 2**3
                if result[ii-1, jj, kk]: accumulator += 2**4
                if kk < stacks - 1:
                    if result[ii-1, jj, kk+1]: accumulator += 2**5
                if jj < cols - 1: 
                    if kk > 0:
                        if result[ii-1, jj+1, kk-1]: accumulator += 2**6
                    if result[ii-1, jj+1, kk]: accumulator += 2**7
                    if kk < stacks - 1:
                        if result[ii-1, jj+1, kk+1]: accumulator += 2**8
             
            if jj > 0:
                if kk > 0:
                    if result[ii, jj-1, kk-1]: accumulator += 2**9
                if result[ii, jj-1, kk]: accumulator += 2**10
                if kk < stacks - 1:
                    if result[ii, jj-1, kk+1]: accumulator += 2**11
            if kk > 0:
                if result[ii, jj, kk-1]: accumulator += 2**12
            if kk < stacks - 1:
                if result[ii, jj, kk+1]: accumulator += 2**14
            if jj < cols - 1:
                if kk > 0:
                    if result[ii, jj+1, kk-1]: accumulator += 2**15
                if result[ii, jj+1, kk]: accumulator +=2**16
                if kk < stacks - 1:
                    if result[ii, jj+1, kk+1]: accumulator += 2**17
            
            if ii < rows - 1:
                if jj > 0:
                    if kk > 0:
                        if result[ii+1, jj-1, kk-1]: accumulator += 2**18
                    if result[ii+1, jj-1, kk]: accumulator += 2**19
                    if kk < stacks - 1: 
                        if result[ii+1, jj-1, kk+1]: accumulator += 2**20
                if kk > 0:
                    if result[ii+1, jj, kk-1]: accumulator += 2**21
                if result[ii+1, jj, kk]: accumulator += 2**22
                if kk < stacks - 1:
                    if result[ii+1, jj, kk+1]: accumulator += 2**23
                if jj < cols - 1:
                    if kk > 0:
                        if result[ii+1, jj+1, kk-1]: accumulator += 2**24
                    if result[ii+1, jj+1, kk]: accumulator += 2**25
                    if kk < stacks - 1:
                        if result[ii+1, jj+1, kk+1]: accumulator += 2**26
            
            # Assign the value of table corresponding to the configuration
            result[ii, jj, kk] = table[accumulator]

def _table_lookup_index(cnp.uint8_t[:, :, ::1] image):
    """
    Return an index into a table per voxel of a binary image

    Take the sum of true neighborhood voxel values where the neighborhood
    looks like this::

       1   2   4
       8  16  32
      64 128 256
      
      2**9   2**10  2**11
      2**12  2**13  2**14
      2**15  2**16  2**17
     
     ...
    """
    cdef:
        Py_ssize_t[:, :, ::1] indexer
        Py_ssize_t *p_indexer
        cnp.uint8_t *p_image
        Py_ssize_t i_stride
        Py_ssize_t j_stride
        Py_ssize_t i_shape
        Py_ssize_t j_shape
        Py_ssize_t k_shape
        Py_ssize_t i
        Py_ssize_t j
        Py_ssize_t k
        Py_ssize_t offset

    i_shape   = image.shape[0]
    j_shape   = image.shape[1]
    k_shape   = image.shape[2]
    indexer = np.zeros((i_shape, j_shape, k_shape), dtype=np.intp)
    p_indexer = &indexer[0, 0, 0]
    p_image   = &image[0, 0, 0]
    i_stride  = image.strides[0]
    j_stride  = image.strides[1]
    
    assert i_shape >= 3 and j_shape >= 3 and k_shape >= 3, \
        "Please use the slow method for arrays < 3x3x3"
    with nogil:
        
        #
        # Do the interior
        #
        
        for i in range(1, i_shape - 1):
            for j in range(1, j_shape - 1):
                offset = i_stride* i + j_stride* j + 1
                for k in range(1, k_shape - 1):
                    if p_image[offset]:
                        p_indexer[offset + i_stride + j_stride + 1] += 1
                        p_indexer[offset + i_stride + j_stride] += 2
                        p_indexer[offset + i_stride + j_stride - 1] += 4
                        p_indexer[offset + i_stride + 1] += 8
                        p_indexer[offset + i_stride] += 16
                        p_indexer[offset + i_stride - 1] += 32
                        p_indexer[offset + i_stride - j_stride + 1] += 64
                        p_indexer[offset + i_stride - j_stride] += 128
                        p_indexer[offset + i_stride - j_stride - 1] += 256
                        ##
                        p_indexer[offset + j_stride + 1] += 2**9
                        p_indexer[offset + j_stride] += 2**10
                        p_indexer[offset + j_stride - 1] += 2**11
                        p_indexer[offset + 1] += 2**12
                        p_indexer[offset] += 2**13
                        p_indexer[offset - 1] += 2**14
                        p_indexer[offset - j_stride + 1] += 2**15
                        p_indexer[offset - j_stride] += 2**16
                        p_indexer[offset - j_stride - 1] += 2**17
                        ##
                        p_indexer[offset - i_stride + j_stride + 1] += 2**18
                        p_indexer[offset - i_stride + j_stride] += 2**19
                        p_indexer[offset - i_stride + j_stride - 1] += 2**20
                        p_indexer[offset - i_stride + 1] += 2**21
                        p_indexer[offset - i_stride] += 2**22
                        p_indexer[offset - i_stride - 1] += 2**23
                        p_indexer[offset - i_stride - j_stride + 1] += 2**24
                        p_indexer[offset - i_stride - j_stride] += 2**25
                        p_indexer[offset - i_stride - j_stride - 1] += 2**26
                    offset += 1
        #
        # Do the corner cases (literally)
        #
        
        if image[0, 0, 0]:
            indexer[0, 0, 0] += 2**13
            indexer[0, 0, 1] += 2**12
            indexer[0, 1, 0] += 2**10
            indexer[0, 1, 1] += 2**9
            indexer[1, 0, 0] += 16
            indexer[1, 0, 1] += 8
            indexer[1, 1, 0] += 2
            indexer[1, 1, 1] += 1

        if image[0, 0, k_shape - 1]:
            indexer[0, 0, k_shape - 2] += 2**14
            indexer[0, 0, k_shape - 1] += 2**13
            indexer[0, 1, k_shape - 2] += 2**11
            indexer[0, 1, k_shape - 1] += 2**10
            indexer[1, 0, k_shape - 2] += 32
            indexer[1, 0, k_shape - 1] += 16
            indexer[1, 1, k_shape - 2] += 4
            indexer[1, 1, k_shape - 1] += 2

        if image[i_shape - 1, 0, 0]:
            indexer[i_shape - 2, 0, 0] += 2**22
            indexer[i_shape - 2, 1, 0] += 2**19
            indexer[i_shape - 1, 0, 0] += 2**13
            indexer[i_shape - 1, 1, 0] += 2**10
            indexer[i_shape - 2, 0, 1] += 2**21
            indexer[i_shape - 2, 1, 1] += 2**18
            indexer[i_shape - 1, 0, 1] += 2**12
            indexer[i_shape - 1, 1, 1] += 2**9
            
        if image[i_shape - 1, 0, k_shape - 1]:
            indexer[i_shape - 2, 0, k_shape - 2] += 2**23
            indexer[i_shape - 2, 1, k_shape - 2] += 2**20
            indexer[i_shape - 1, 0, k_shape - 2] += 2**14
            indexer[i_shape - 1, 1, k_shape - 2] += 2**11
            indexer[i_shape - 2, 0, k_shape - 1] += 2**22
            indexer[i_shape - 2, 1, k_shape - 1] += 2**19
            indexer[i_shape - 1, 0, k_shape - 1] += 2**13
            indexer[i_shape - 1, 1, k_shape - 1] += 2**10
            
        if image[0, j_shape - 1, 0]:
            indexer[0, j_shape - 2, 0] += 2**16
            indexer[0, j_shape - 1, 0] += 2**13
            indexer[1, j_shape - 2, 0] += 2**7
            indexer[1, j_shape - 1, 0] += 2**4
            indexer[0, j_shape - 2, 1] += 2**15
            indexer[0, j_shape - 1, 1] += 2**12
            indexer[1, j_shape - 2, 1] += 2**6
            indexer[1, j_shape - 1, 1] += 2**3

        if image[i_shape - 1, j_shape - 1, 0]:
            indexer[i_shape - 2, j_shape - 2, 0] += 2**25
            indexer[i_shape - 2, j_shape - 1, 0] += 2**22
            indexer[i_shape - 1, j_shape - 2, 0] += 2**16
            indexer[i_shape - 1, j_shape - 1, 0] += 2**13
            indexer[i_shape - 2, j_shape - 2, 1] += 2**24
            indexer[i_shape - 2, j_shape - 1, 1] += 2**21
            indexer[i_shape - 1, j_shape - 2, 1] += 2**15
            indexer[i_shape - 1, j_shape - 1, 1] += 2**12
            
        if image[i_shape - 1, j_shape - 1, k_shape - 1]:
            indexer[i_shape - 2, j_shape - 2, k_shape - 2] += 2**26
            indexer[i_shape - 2, j_shape - 1, k_shape - 2] += 2**23
            indexer[i_shape - 1, j_shape - 2, k_shape - 2] += 2**17
            indexer[i_shape - 1, j_shape - 1, k_shape - 2] += 2**14
            indexer[i_shape - 2, j_shape - 2, k_shape - 1] += 2**25
            indexer[i_shape - 2, j_shape - 1, k_shape - 1] += 2**22
            indexer[i_shape - 1, j_shape - 2, k_shape - 1] += 2**16
            indexer[i_shape - 1, j_shape - 1, k_shape - 1] += 2**13
            
        if image[0, j_shape - 1, k_shape - 1]:
            indexer[0, j_shape - 2, k_shape - 2] += 2**17
            indexer[0, j_shape - 1, k_shape - 2] += 2**14
            indexer[1, j_shape - 2, k_shape - 2] += 2**8
            indexer[1, j_shape - 1, k_shape - 2] += 2**5
            indexer[0, j_shape - 2, k_shape - 1] += 2**16
            indexer[0, j_shape - 1, k_shape - 1] += 2**13
            indexer[1, j_shape - 2, k_shape - 1] += 2**7
            indexer[1, j_shape - 1, k_shape - 1] += 2**4
        #
        # Do the edges
        #
        
        for j in range(1, j_shape - 1):
            if image[0, j, 0]:
                indexer[0, j - 1, 0] += 2**16
                indexer[0, j, 0] += 2**13
                indexer[0, j + 1, 0] += 2**10
                indexer[0, j - 1, 1] += 2**15
                indexer[0, j, 1] += 2**12
                indexer[0, j + 1, 1] += 2**9
                indexer[1, j - 1, 0] += 2**7
                indexer[1, j, 0] += 2**4
                indexer[1, j + 1, 0] += 2**1
                indexer[1, j - 1, 1] += 2**6
                indexer[1, j, 1] += 2**3
                indexer[1, j + 1, 1] += 2**0
            if image[0, j, k_shape - 1]:
                indexer[0, j - 1, k_shape - 2] += 2**17
                indexer[0, j, k_shape - 2] += 2**14
                indexer[0, j + 1, k_shape - 2] += 2**11
                indexer[1, j - 1, k_shape - 2] += 2**8
                indexer[1, j, k_shape - 2] += 2**5
                indexer[1, j + 1,k_shape - 2] += 2**2
                indexer[0, j - 1, k_shape - 1] += 2**16
                indexer[0, j, k_shape - 1] += 2**13
                indexer[0, j + 1, k_shape - 1] += 2**10
                indexer[1, j - 1, k_shape - 1] += 2**7
                indexer[1, j, k_shape - 1] += 2**4
                indexer[1, j + 1, k_shape - 1] += 2**1
            if image[i_shape - 1, j, 0]:
                indexer[i_shape - 2, j - 1, 0] += 2**25
                indexer[i_shape - 2, j, 0] += 2**22
                indexer[i_shape - 2, j + 1, 0] += 2**19
                indexer[i_shape - 1, j - 1, 0] += 2**16
                indexer[i_shape - 1, j, 0] += 2**13
                indexer[i_shape - 1, j + 1, 0] += 2**10
                indexer[i_shape - 2, j - 1, 1] += 2**24
                indexer[i_shape - 2, j, 1] += 2**21
                indexer[i_shape - 2, j + 1, 1] += 2**18
                indexer[i_shape - 1, j - 1, 1] += 2**15
                indexer[i_shape - 1, j, 1] += 2**12
                indexer[i_shape - 1, j + 1, 1] += 2**9
            if image[i_shape - 1, j, k_shape - 1]:
                indexer[i_shape - 2, j - 1, k_shape - 2] += 2**26
                indexer[i_shape - 2, j, k_shape - 2] += 2**23
                indexer[i_shape - 2, j + 1, k_shape - 2] += 2**20
                indexer[i_shape - 1, j - 1, k_shape - 2] += 2**17
                indexer[i_shape - 1, j, k_shape - 2] += 2**14
                indexer[i_shape - 1, j + 1, k_shape - 2] += 2**11
                indexer[i_shape - 2, j - 1, k_shape - 1] += 2**25
                indexer[i_shape - 2, j, k_shape - 1] += 2**22
                indexer[i_shape - 2, j + 1, k_shape - 1] += 2**19
                indexer[i_shape - 1, j - 1, k_shape - 1] += 2**16
                indexer[i_shape - 1, j, k_shape - 1] += 2**13
                indexer[i_shape - 1, j + 1, k_shape - 1] += 2**10

        for i in range(1, i_shape - 1):
            if image[i, 0, 0]:
                indexer[i - 1, 0, 0] += 2**22
                indexer[i, 0, 0] += 2**13
                indexer[i + 1, 0, 0] += 2**4
                indexer[i - 1, 1, 0] += 2**19
                indexer[i, 1, 0] += 2**10
                indexer[i + 1, 1, 0] += 2**1
                indexer[i - 1, 0, 1] += 2**21
                indexer[i, 0, 1] += 2**12
                indexer[i + 1, 0, 1] += 2**3
                indexer[i - 1, 1, 1] += 2**18
                indexer[i, 1, 1] += 2**9
                indexer[i + 1, 1, 1] += 2**0
            if image[i, 0, k_shape - 1]:
                indexer[i - 1, 0, k_shape - 2] += 2**23
                indexer[i, 0, k_shape - 2] += 2**14
                indexer[i + 1, 0, k_shape - 2] += 2**5
                indexer[i - 1, 1, k_shape - 2] += 2**20
                indexer[i, 1, k_shape - 2] += 2**11
                indexer[i + 1, 1, k_shape - 2] += 2**2
                indexer[i - 1, 0, k_shape - 1] += 2**22
                indexer[i, 0, k_shape - 1] += 2**13
                indexer[i + 1, 0, k_shape - 1] += 2**4
                indexer[i - 1, 1, k_shape - 1] += 2**19
                indexer[i, 1, k_shape - 1] += 2**10
                indexer[i + 1, 1, k_shape - 1] += 2**1
            if image[i, j_shape - 1 , 0]:
                indexer[i - 1, j_shape - 2, 0] += 2**25
                indexer[i, j_shape - 2, 0] += 2**16
                indexer[i + 1, j_shape - 2, 0] += 2**7
                indexer[i - 1, j_shape - 1, 0] += 2**22
                indexer[i, j_shape - 1, 0] += 2**13
                indexer[i + 1, j_shape - 1, 0] += 2**4
                indexer[i - 1, j_shape - 2, 1] += 2**24
                indexer[i, j_shape - 2, 1] += 2**15
                indexer[i + 1, j_shape - 2, 1] += 2**6
                indexer[i - 1, j_shape - 1, 1] += 2**21
                indexer[i, j_shape - 1, 1] += 2**12
                indexer[i + 1, j_shape - 1, 1] += 2**3
            if image[i, j_shape - 1, k_shape - 1]:
                indexer[i - 1, j_shape - 2, k_shape - 2] += 2**26
                indexer[i, j_shape - 2, k_shape - 2] += 2**17
                indexer[i + 1, j_shape - 2, k_shape - 2] += 2**8
                indexer[i - 1, j_shape - 1, k_shape - 2] += 2**23
                indexer[i, j_shape - 1, k_shape - 2] += 2**14
                indexer[i + 1, j_shape - 1, k_shape - 2] += 2**5
                indexer[i - 1, j_shape - 2, k_shape - 1] += 2**25
                indexer[i, j_shape - 2, k_shape - 1] += 2**16
                indexer[i + 1, j_shape - 2, k_shape - 1] += 2**7
                indexer[i - 1, j_shape - 1, k_shape - 1] += 2**22
                indexer[i, j_shape - 1, k_shape - 1] += 2**13
                indexer[i + 1, j_shape - 1, k_shape - 1] += 2**4
                
        for k in range(1, k_shape - 1):
            if image[0, 0, k]:
                indexer[0, 0, k - 1] += 2**14
                indexer[0, 0, k] += 2**13
                indexer[0, 0, k + 1] += 2**12
                indexer[1, 0, k - 1] += 2**5
                indexer[1, 0, k] += 2**4
                indexer[1, 0, k + 1] += 2**3
                indexer[0, 1, k - 1] += 2**11
                indexer[0, 1, k] += 2**10
                indexer[0, 1, k + 1] += 2**9
                indexer[1, 1, k - 1] += 2**2
                indexer[1, 1, k] += 2**1
                indexer[1, 1, k + 1] += 2**0
            if image[0, j_shape - 1, k]:
                indexer[0, j_shape - 2, k - 1] += 2**17
                indexer[0, j_shape - 2, k] += 2**16
                indexer[0, j_shape - 2, k + 1] += 2**15
                indexer[1, j_shape - 2, k - 1] += 2**8
                indexer[1, j_shape - 2, k] += 2**7
                indexer[1, j_shape - 2, k + 1] += 2**6
                indexer[0, j_shape - 1, k - 1] += 2**14
                indexer[0, j_shape - 1, k] += 2**13
                indexer[0, j_shape - 1, k + 1] += 2**12
                indexer[1, j_shape - 1, k - 1] += 2**5
                indexer[1, j_shape - 1, k] += 2**4
                indexer[1, j_shape - 1, k + 1] += 2**3
            if image[i_shape - 1, 0, k]:
                indexer[i_shape - 2, 0, k - 1] += 2**23
                indexer[i_shape - 2, 0, k] += 2**22
                indexer[i_shape - 2, 0, k + 1] += 2**21
                indexer[i_shape - 1, 0, k - 1] += 2**14
                indexer[i_shape - 1, 0, k] += 2**13
                indexer[i_shape - 1, 0, k + 1] += 2**12
                indexer[i_shape - 2, 1, k - 1] += 2**20
                indexer[i_shape - 2, 1, k] += 2**19
                indexer[i_shape - 2, 1, k + 1] += 2**18
                indexer[i_shape - 1, 1, k - 1] += 2**11
                indexer[i_shape - 1, 1, k] += 2**10
                indexer[i_shape - 1, 1, k + 1] += 2**9
            if image[i_shape - 1, j_shape - 1, k]:
                indexer[i_shape - 2, j_shape - 2, k - 1] += 2**26
                indexer[i_shape - 2, j_shape - 2, k] += 2**25
                indexer[i_shape - 2, j_shape - 2, k + 1] += 2**24
                indexer[i_shape - 1, j_shape - 2, k - 1] += 2**17
                indexer[i_shape - 1, j_shape - 2, k] += 2**16
                indexer[i_shape - 1, j_shape - 2, k + 1] += 2**15
                indexer[i_shape - 2, j_shape - 1, k - 1] += 2**23
                indexer[i_shape - 2, j_shape - 1, k] += 2**22
                indexer[i_shape - 2, j_shape - 1, k + 1] += 2**21
                indexer[i_shape - 1, j_shape - 1, k - 1] += 2**14
                indexer[i_shape - 1, j_shape - 1, k ] += 2**13
                indexer[i_shape - 1, j_shape - 1, k + 1] += 2**12
                
        #
        # Do the faces
        #
                
        for j in range(1, j_shape - 1):
            for k in range(1, k_shape - 1):
                if image[0, j, k]:
                    indexer[0, j-1, k-1] += 2**17
                    indexer[0, j-1, k] += 2**16
                    indexer[0, j-1, k+1] += 2**15
                    indexer[0, j, k-1] += 2**14
                    indexer[0, j, k] += 2**13
                    indexer[0, j, k+1] += 2**12
                    indexer[0, j+1, k-1] += 2**11
                    indexer[0, j+1, k] += 2**10
                    indexer[0, j+1, k+1] += 2**9
                    indexer[1, j-1, k-1] += 2**8
                    indexer[1, j-1, k] += 2**7
                    indexer[1, j-1, k+1] += 2**6
                    indexer[1, j, k-1] += 2**5
                    indexer[1, j, k] += 2**4
                    indexer[1, j, k+1] += 2**3
                    indexer[1, j+1, k-1] += 2**2
                    indexer[1, j+1, k] += 2**1
                    indexer[1, j+1, k+1] += 2**0
                    
        for i in range(1, i_shape - 1):
            for k in range(1, k_shape - 1):
                if image[i, 0, k]:
                    indexer[i-1, 0, k-1] += 2**23
                    indexer[i-1, 0, k] += 2**22
                    indexer[i-1, 0, k+1] += 2**21
                    indexer[i-1, 1, k-1] += 2**20
                    indexer[i-1, 1, k] += 2**19
                    indexer[i-1, 1, k+1] += 2**18
                    indexer[i, 0, k-1] += 2**14
                    indexer[i, 0, k] += 2**13
                    indexer[i, 0, k+1] += 2**12
                    indexer[i, 1, k-1] += 2**11
                    indexer[i, 1, k] += 2**10
                    indexer[i, 1, k+1] += 2**9
                    indexer[i+1, 0, k-1] += 2**5
                    indexer[i+1, 0, k] += 2**4
                    indexer[i+1, 0, k+1] += 2**3
                    indexer[i+1, 1, k-1] += 2**2
                    indexer[i+1, 1, k] += 2**1
                    indexer[i+1, 1, k+1] += 2**0
                    
        for i in range(1, i_shape - 1):
            for j in range(1, j_shape - 1):
                if image[i, j, 0]:
                    indexer[i-1, j-1, 0] += 2**25
                    indexer[i-1, j-1, 1] += 2**24
                    indexer[i-1, j, 0] += 2**22
                    indexer[i-1, j, 1] += 2**21
                    indexer[i-1, j+1, 0] += 2**19
                    indexer[i-1, j+1, 1] += 2**18
                    indexer[i, j-1, 0] += 2**16
                    indexer[i, j-1, 1] += 2**15
                    indexer[i, j, 0] += 2**13
                    indexer[i, j, 1] += 2**12
                    indexer[i, j+1, 0] += 2**10
                    indexer[i, j+1, 1] += 2**9
                    indexer[i+1, j-1, 0] += 2**7
                    indexer[i+1, j-1, 1] += 2**6
                    indexer[i+1, j, 0] += 2**4
                    indexer[i+1, j, 1] += 2**3
                    indexer[i+1, j+1, 0] += 2**1
                    indexer[i+1, j+1, 1] += 2**0
       
        for i in range(1, i_shape - 1):
            for j in range(1, j_shape - 1):
                if image[i, j, k_shape - 1]:
                    indexer[i-1, j-1, k_shape - 2] += 2**26
                    indexer[i-1, j-1, k_shape - 1] += 2**25
                    indexer[i-1, j, k_shape - 2] += 2**23
                    indexer[i-1, j, k_shape - 1] += 2**22
                    indexer[i-1, j+1, k_shape - 2] += 2**20
                    indexer[i-1, j+1, k_shape - 1] += 2**19
                    indexer[i, j-1, k_shape - 2] += 2**17
                    indexer[i, j-1, k_shape - 1] += 2**16
                    indexer[i, j, k_shape - 2] += 2**14
                    indexer[i, j, k_shape - 1] += 2**13
                    indexer[i, j+1, k_shape - 2] += 2**11
                    indexer[i, j+1, k_shape - 1] += 2**10
                    indexer[i+1, j-1, k_shape - 2] += 2**8
                    indexer[i+1, j-1, k_shape - 1] += 2**7
                    indexer[i+1, j, k_shape - 2] += 2**5
                    indexer[i+1, j, k_shape - 1] += 2**4
                    indexer[i+1, j+1, k_shape - 2] += 2**2
                    indexer[i+1, j+1, k_shape - 1] += 2**1
                    
        for i in range(1, i_shape - 1):
            for k in range(1, k_shape - 1):
                if image[i, j_shape - 1, k]:
                    indexer[i-1, j_shape-2, k-1] += 2**26
                    indexer[i-1, j_shape-2, k] += 2**25
                    indexer[i-1, j_shape-2, k+1] += 2**24
                    indexer[i-1, j_shape-1, k-1] += 2**23
                    indexer[i-1, j_shape-1, k] += 2**22
                    indexer[i-1, j_shape-1, k+1] += 2**21
                    indexer[i, j_shape-2, k-1] += 2**17
                    indexer[i, j_shape-2, k] += 2**16
                    indexer[i, j_shape-2, k+1] += 2**15
                    indexer[i, j_shape-1, k-1] += 2**14
                    indexer[i, j_shape-1, k] += 2**13
                    indexer[i, j_shape-1, k+1] += 2**12
                    indexer[i+1, j_shape-2, k-1] += 2**8
                    indexer[i+1, j_shape-2, k] += 2**7
                    indexer[i+1, j_shape-2, k+1] += 2**6
                    indexer[i+1, j_shape-1, k-1] += 2**5
                    indexer[i+1, j_shape-1, k] += 2**4
                    indexer[i+1, j_shape-1, k+1] += 2**3
                    
        for j in range(1, j_shape - 1):
            for k in range(1, k_shape - 1):
                if image[i_shape - 1, j, k]:
                    indexer[i_shape - 2, j-1, k-1] += 2**26
                    indexer[i_shape - 2, j-1, k] += 2**25
                    indexer[i_shape - 2, j-1, k+1] += 2**24
                    indexer[i_shape - 2, j, k-1] += 2**23
                    indexer[i_shape - 2, j, k] += 2**22
                    indexer[i_shape - 2, j, k+1] += 2**21
                    indexer[i_shape - 2, j+1, k-1] += 2**20
                    indexer[i_shape - 2, j+1, k] += 2**19
                    indexer[i_shape - 2, j+1, k+1] += 2**18
                    indexer[i_shape - 1, j-1, k-1] += 2**17
                    indexer[i_shape - 1, j-1, k] += 2**16
                    indexer[i_shape - 1, j-1, k+1] += 2**15
                    indexer[i_shape - 1, j, k-1] += 2**14
                    indexer[i_shape - 1, j, k] += 2**13
                    indexer[i_shape - 1, j, k+1] += 2**12
                    indexer[i_shape - 1, j+1, k-1] += 2**11
                    indexer[i_shape - 1, j+1, k] += 2**10
                    indexer[i_shape - 1, j+1, k+1] += 2**9
                
    return np.asarray(indexer)
