#!/usr/bin/env python
# coding: utf-8

from setuptools import setup, find_packages

setup(name='alone',
      install_requires=[
        'pandas', 'cython','graphbrain'   ],
      url = 'https://github.com/nicolamelluso/graphbrain', download_url = 'https://github.com/nicolamelluso/graphbrain', dependency_links = ["https://github.com/graphbrain/graphbrain#egg=graphrain"])



