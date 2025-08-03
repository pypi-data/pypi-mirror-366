#!/usr/bin/env python
# -*- coding:utf-8 -*-
# Author: Zzz(1309458652@qq.com)
# Description:

from setuptools import setup, find_packages

setup(
    name = 'key_musicz_res',
    version = '0.1.1',
    keywords='key_musicz_res',
    long_description=open('README.md', 'r', encoding="utf-8").read(),
    long_description_content_type='text/markdown',
    description = "键盘弹钢琴，keyboard to play piano",
    license = 'MIT License',
    url = 'https://github.com/buildCodeZ/key_musicz_res',
    author = 'Zzz',
    author_email = '1309458652@qq.com',
    packages = find_packages(),
    include_package_data = True,
    platforms = 'any',
    install_requires = ['key_musicz>=0.2.1'],
)
