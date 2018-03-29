from distutils.core import setup
from Cython.Build import cythonize

setup(
    name = 'Test maths',
    ext_modules = cythonize("picam/cmaths.pyx"),
)

