import os
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

modules = [Extension(name='jwoanda.resizebyvolume', sources=['jwoanda/resizebyvolume.pyx']),
           Extension(name='jwoanda.portfolio.analysisfcn', sources=['jwoanda/portfolio/analysisfcn.pyx'])]

setup(
    name = "jwoanda",
    version = "0.0.1",
    author = "Jean Wicht",
    author_email = "jean.wicht@gmail.com",
    description = ("Trading framework for OANDA v20 rest API"),
    license = "GPLv2",
    keywords = "oanda forex trading",
    #url = "http://packages.python.org/an_example_pypi_project",
    packages=find_packages(),
    long_description=read('README.md'),
    install_requires=[
        'numpy',
        'matplotlib',
        'pandas',
        'TA-lib',
        'cython'
    ],
    classifiers=[
        "Development Status :: 3 - Alpha",
        "Topic :: Utilities"
    ],
    cmdclass={'build_ext':build_ext},
    ext_modules = modules
)
