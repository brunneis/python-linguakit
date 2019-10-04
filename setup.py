#!/usr/bin/env python
# -*- coding: utf-8 -*-

from setuptools import setup
import linguakit

setup(name='linguakit',
      version=linguakit.__version__,
      description='Python wrapper for Linguakit\'s Perl implementation',
      url='https://github.com/brunneis/python-linguakit',
      author='Rodrigo Martínez',
      author_email='dev@brunneis.com',
      license='GNU General Public License v3.0',
      packages=['linguakit'],
      zip_safe=False,
      classifiers=[
          "Development Status :: 4 - Beta",
          "Environment :: Console",
          "Intended Audience :: Developers",
          "License :: OSI Approved :: GNU General Public License v3 (GPLv3)",
          "Operating System :: POSIX :: Linux",
          "Programming Language :: Python :: 3.6",
          "Programming Language :: Python :: Implementation :: PyPy",
          "Topic :: Software Development :: Libraries :: Python Modules",
      ],
      install_requires=['pexpect'])
