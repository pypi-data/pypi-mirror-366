import sys
try:
    from setuptools import setup, Extension
except ImportError:
    from distutils.core import setup, Extension

import numpy as np

if sys.platform != 'win32':
    compile_args = ['-funroll-loops']
else:
    compile_args = []

with open("README.md", "r") as f:
    long_desc = f.read()

with open("zebranoise/_version.py", "r") as f:
    exec(f.read())

setup(
    name='zebranoise',
    version=__version__,
    description='Zebra noise stimuli for Python',
    long_description = long_desc,
    long_description_content_type='text/markdown',
    author='Max Shinn',
    author_email='m.shinn@ucl.ac.uk',
    url='https://github.com/mwshinn/zebra_noise',
    classifiers = [
        'Development Status :: 4 - Beta',
        'Programming Language :: C',
        'Programming Language :: Python :: 3',
        'Intended Audience :: Science/Research',
        'License :: OSI Approved :: MIT License',
        'Topic :: Multimedia :: Graphics',
        'Topic :: Scientific/Engineering',
    ],
    install_requires = ['numpy', 'imageio', 'imageio-ffmpeg', 'tqdm'],
    packages=['zebranoise'],
    ext_modules=[
        Extension('zebranoise._perlin', ['zebranoise/_perlin.c'],
            extra_compile_args=compile_args,
                  include_dirs=[np.get_include()],
        )
    ],
)
