#!/usr/bin/env python
# coding=utf-8

from setuptools import setup, find_packages

# To use a consistent encoding
from codecs import open
from os import path

here = path.abspath(path.dirname(__file__))

# Get the long description from the README file
with open(path.join(here, 'README.md'), encoding='utf-8') as f:
    long_description = f.read()

setup(
    name='PyFronius',
    version='0.4.3',
    description='Automated JSON API based communication with Fronius Symo',
    author='Niels Mündler, Gerrit Beine',
    author_email='n.muendler@web.de, mail@gerritbeine.de',
    url='https://github.com/nielstron/pyfronius/',
    py_modules=['pyfronius'],
    package_data={'pyfronius.tests.test_structure': ['solar_api/v1/*.fcgi*', 'solar_api/v1/*.cgi*', '.error.html']},
    packages=find_packages(),
    install_requires=[
        'async_timeout',
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
        'Programming Language :: Python :: 3.5',
        'Programming Language :: Python :: 3.6',
        'Programming Language :: Python :: 3.7',
    ],
    keywords='python fronius json api solar photovoltaics pv',
    python_requires='>=3',
    test_suite='pyfronius.tests',
)
