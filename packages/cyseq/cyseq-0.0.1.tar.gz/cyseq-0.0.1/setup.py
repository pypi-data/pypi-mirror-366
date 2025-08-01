#!/usr/bin/env python

import setuptools
from Cython.Build import cythonize


extensions = [
    setuptools.Extension("cyseq._seq", ["src/cyseq/_seq.pyx"], language="c++"),
]

if __name__ == "__main__":
    setuptools.setup(ext_modules=cythonize(extensions))
