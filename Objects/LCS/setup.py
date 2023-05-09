'''
Author:        James Parkington
Created Date:  5/8/2023
Modified Date: 5/8/2023

This setup.py file is responsible for building and compiling the Cython module lcs_cython.pyx.
It imports the necessary modules to configure and build the Cython extension.

The following modules are imported for specific purposes:
- setuptools: Used to provide build and distribution tools for the Cython module.
- Cython.Build: Provides the cythonize function to convert the .pyx file to a C extension.
- numpy: Required to include NumPy headers during the compilation process.

To build and compile the lcs_cython module, run the following command in your terminal:
python setup.py build_ext --inplace
'''

from   setuptools   import setup
from   Cython.Build import cythonize
import numpy as np

setup(ext_modules  = cythonize("lcs_cython.pyx", language_level = 3),
      include_dirs = [np.get_include()])