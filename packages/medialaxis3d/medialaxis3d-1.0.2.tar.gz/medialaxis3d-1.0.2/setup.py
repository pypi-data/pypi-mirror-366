from setuptools import Extension, setup
from Cython.Build import cythonize
import numpy

extensions = [
    Extension(name = "skeletonize_cy",
              sources = ["medialaxis3d/skeletonize_cy.pyx"],
              define_macros=[('NPY_NO_DEPRECATED_API', 'NPY_1_7_API_VERSION')],
              include_dirs = [numpy.get_include()]),
]

setup(
    ext_modules = cythonize(extensions,
                            compiler_directives={"language_level": 3},
                            force = True),
)
