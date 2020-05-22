#!/usr/bin/env python
# coding: utf-8

from setuptools import setup, find_packages

setup(
    name='graphbrain',
    dependency_links = [
     "git+git://github.com/graphbrain/graphbrain#egg=graphbrain",
    ]
    include_package_data=True,
)

