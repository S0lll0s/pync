#!/usr/bin/env python
# vim:fileencoding=utf-8:noet
from __future__ import unicode_literals
import os
import sys

from setuptools import setup, find_packages
from setuptools.command.install import install

here = os.path.abspath(os.path.dirname(__file__))
try:
    README = open(os.path.join(here, "README.md"), "rb").read().decode("utf-8")
except IOError:
    README = ""

setup(
    name="pync",
    version="0.1",
    description="pync is a utility to sync parts of a folder to a (usually) smaller medium",
    long_description=README,
    author="Sol Bekic",
    author_email="s0lll0s@blinkenshell.org",
    url="https://github.com/S0lll0s/pync",
    scripts=["scripts/pync"],
    license="MIT",
    packages=find_packages(exclude=("tests", "tests.*")),
    include_package_data=True,
    install_requires=["colorize"]
)
