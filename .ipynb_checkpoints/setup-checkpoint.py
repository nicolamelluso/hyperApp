#!/usr/bin/env python
# coding: utf-8

from setuptools import setup, find_packages

import os
thelibFolder = os.path.dirname(os.path.realpath(__file__))
requirementPath = thelibFolder + '/reqs.txt'
install_requires = ['pandas'] # Examples: ["gunicorn", "docutils>=0.3", "lxml==0.5a7"]
if os.path.isfile(requirementPath):
    with open(requirementPath) as f:
        install_requires = f.read().splitlines()
setup(name="alone", install_requires=install_requires)


