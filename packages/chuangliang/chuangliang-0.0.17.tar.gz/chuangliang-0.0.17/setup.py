#!/usr/bin/env python3
# coding = utf8
"""
@ Author : ZeroSeeker
@ e-mail : zeroseeker@foxmail.com
@ GitHub : https://github.com/ZeroSeeker
@ Gitee : https://gitee.com/ZeroSeeker
"""
import setuptools

with open("README.md", "r", encoding='utf-8') as fh:
    long_description = fh.read()

setuptools.setup(
    name="chuangliang",
    version="0.0.17",
    author="ZeroSeeker",
    author_email="zeroseeker@foxmail.com",
    description="创量广告平台SDK",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://gitee.com/ZeroSeeker/chuangliang",
    packages=setuptools.find_packages(),
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    install_requires=[
        'lazysdk>=0.1.89'
    ]
)
