import os
import sys
from setuptools import setup, find_packages

# Utility function to read the README file.
# Used for the long_description.  It's nice, because now 1) we have a top level
# README file and 2) it's easier to type in the README file than to put a raw
# string in below ...
def read(fname):
    return open(os.path.join(os.path.dirname(__file__), fname)).read()

from distutils.extension import Extension
from Cython.Distutils import build_ext

README_FILE = os.path.join(os.path.dirname(__file__), 'README.md')

modules = []
for root, dirs, files in os.walk("jwoanda/"):
       for f in files:
           if f.endswith('.pyx'):
               pyx = root + "/" + f
               name = pyx.replace('/', '.').replace('.pyx', '')
               modules.append(Extension(name=name, sources=[pyx]))

install_requires=[
    'numpy',
    'matplotlib',
    'pandas',
    'pathlib2',
    'progressbar2',
    'scipy',
    'six',
    'TA-lib',
    'v20',
    'pyxdg',
    'PyYAML'
    ]

if sys.version_info.major < 3:
    install_requires.append('backports_abc')
    install_requires.append('backports.lzma')
               
setup(
    name = "jwoanda",
    version = "0.0.2",
    author = "Jean Wicht",
    author_email = "jean.wicht@gmail.com",
    description = ("Trading framework for OANDA v20 rest API"),
    license = "GPLv2",
    keywords = "oanda forex trading",
    packages=find_packages(),
    long_description=read('README.md'),
    install_requires=install_requires,
    classifiers=[
        "Development Status :: 3 - Alpha",
        "Topic :: Utilities"
    ],
    cmdclass={'build_ext': build_ext},
    ext_modules = modules
)
