#!/usr/bin/env python3
"""
Argslib
=======

A minimalist library for parsing command line arguments.

"""

from setuptools import setup

setup(
    name = 'argslib',
    version = '0.2.1',
    py_modules = ['args'],
    author = 'Darren Mulholland',
    url = 'https://github.com/dmulholl/argslib',
    license = 'Public Domain',
    description = (
        'A minimalist argument-parsing library.'
    ),
    long_description = __doc__,
    classifiers = [
        'Programming Language :: Python :: 3',
        'Operating System :: OS Independent',
        'License :: Public Domain',
    ],
)
