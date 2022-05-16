#!/usr/bin/python
# -*- coding:utf-8 -*-

from setuptools import setup, find_packages


def install_requires():
    """
    Return requires in requirements.txt
    :return:
    """
    try:
        with open("requirements.txt") as f:
            return [line.strip() for line in f.readlines() if line.strip()]
    except OSError:
        return []


VERSION = '1.0.0'
AUTHOR = "msga"
AUTHOR_EMAIL = "galoliy@foxmail.com"
URL = "https://www.github.com/ShichaoMa/toolkit"
NAME = "msgs-comm"
DESCRIPTION = "msga common , simple tools. "
KEYWORDS = "tools function"
LICENSE = "MIT"


setup(
    name=NAME,
    version=VERSION,
    description=DESCRIPTION,
    classifiers=[
        'License :: OSI Approved :: MIT License',
        'Programming Language :: Python',
        'Intended Audience :: Developers',
        'Operating System :: OS Independent',
    ],
    keywords=KEYWORDS,
    author=AUTHOR,
    author_email=AUTHOR_EMAIL,
    url=URL,
    license=LICENSE,
    packages=find_packages(exclude=("tests*",)),
    install_requires=install_requires(),
    include_package_data=True,
    zip_safe=True,
    setup_requires=["pytest-runner"],
    tests_require=["pytest-apistellar", "pytest-asyncio", "pytest-cov"]
)