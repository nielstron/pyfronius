#!/usr/bin/env python
# coding=utf-8

from setuptools import setup, find_packages

# To use a consistent encoding
from codecs import open
from os import path

here = path.abspath(path.dirname(__file__))

# Get the long description from the README file
with open(path.join(here, "README.md"), encoding="utf-8") as f:
    long_description = f.read()

setup(
    name="PyFronius",
    version="0.8.0",
    description="Automated API based communication with Fronius Inverters",
    author="Niels Mündler, Gerrit Beine, Derek Caudwell",
    author_email="n.muendler@web.de, mail@gerritbeine.de",
    url="https://github.com/nielstron/pyfronius/",
    packages=find_packages(exclude=("pyfronius.tests", "pyfronius.tests.*")),
    install_requires=["aiohttp"],
    long_description=long_description,
    long_description_content_type="text/markdown",
    license="MIT",
    classifiers=[
        "Development Status :: 3 - Alpha",
        "Intended Audience :: Developers",
        "Topic :: Software Development :: Object Brokering",
        "License :: OSI Approved :: MIT License",
        "Programming Language :: Python :: 3.10",
    ],
    keywords="python fronius json api solar photovoltaics pv",
    python_requires=">=3.10",
    test_suite="pyfronius.tests",
)
