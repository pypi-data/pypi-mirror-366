#!/usr/bin/env python3
"""
Setup script for the FernetKeyVault package.
"""

from setuptools import setup, find_packages

# Read the content of README.md for the long description
with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

setup(
    name="FernetKeyVault",
    version="1.0.2",
    author="Rajarajan Veerichetty",
    author_email="rajarajan.v@gmail.com",
    description="A simple Python SQLite3-based key-value storage vault",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/kvcrajan/FernetKeyVault",
    project_urls={
        "Bug Tracker": "https://github.com/kvcrajan/FernetKeyVault/issues",
    },
    packages=find_packages(),
    python_requires=">=3.8",
)