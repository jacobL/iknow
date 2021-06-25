# -*- coding: utf-8 -*-
"""
Created on Mon Mar 22 15:12:19 2021

@author: jenny
"""

from distutils.core import setup
from Cython.Build import cythonize

setup(name='QS_model', ext_modules=cythonize('QS_model_simple.py'))