#!/usr/bin/env python
# coding=utf-8

from setuptools import setup

# To use a consistent encoding
from codecs import open
from os import path

here = path.abspath(path.dirname(__file__))

# Get the long description from the README file
with open(path.join(here, 'README.md'), encoding='utf-8') as f:
    long_description = f.read()

setup(name='PyFronius',
      version='0.1',
      description='Automated JSON API based communication with Fronius Symo',
      author='Niels Mündler',
      author_email='n.muendler@web.de',
      url='https://github.com/nielstron/pyfronius/',
      py_modules=['pyfronius'],
      requires= [
          'json',
          'requests'
          ],
      long_description=long_description,
      license='MIT',
      classifiers=[
        'Development Status :: 3 - Alpha',
        # Indicate who your project is intended for
        'Intended Audience :: Developers',
        'Topic :: Software Development :: Object Brokering',
    
        # Pick your license as you wish (should match "license" above)
         'License :: OSI Approved :: MIT License',
    
        # Specify the Python versions you support here. In particular, ensure
        # that you indicate whether you support Python 2, Python 3 or both.
        'Programming Language :: Python :: 3.6'
        ],
      keywords='python fronius json api solar photovoltaic pv',
      python_requires='>=3',
     )
