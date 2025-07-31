#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# @File     : setup
# @Author   : LiuYan
# @Time     : 2021/4/16 10:07

import setuptools

with open('README.md', 'r', encoding='utf-8') as fh:
    long_description = fh.read()

setuptools.setup(
    name='daring',
    version='1.2.0.2',
    author='Raodi',
    author_email='raodi@qq.com',
    description='The daring is a collection of Python scripts that focuses on providing a range of efficient and flexible translation tool functions. ',
    long_description=long_description,
    long_description_content_type='text/markdown',
    url='https://gitee.com/Raodi/daring',
    packages=setuptools.find_packages(),
    classifiers=[
        'Programming Language :: Python :: 3',
        'License :: OSI Approved :: MIT License',
        'Operating System :: OS Independent',
    ],
)

