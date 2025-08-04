# -*- coding: utf-8 -*-

from setuptools import setup, find_packages

with open("README.rst") as f:
    _readme = f.read()

with open("LICENSE") as f:
    _license = f.read()

setup(
    name="pyeutils",
    version="0.0.1",
    description="NCBI E-utilities Client",
    long_description_content_type="text/x-rst",
    long_description=_readme,
    author="Filipe Liu",
    author_email="fliu@anl.gov",
    url="https://github.com/Fxe/pyeutils",
    license="MIT",
    packages=find_packages(exclude=("docs")),
    classifiers=[
        "Development Status :: 3 - Alpha",
        "Topic :: Scientific/Engineering :: Bio-Informatics",
        "Intended Audience :: Science/Research",
        "Operating System :: OS Independent",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "Natural Language :: English",
    ],
    install_requires=[
        "requests >= 2.0.0",
    ],
    tests_require=[
        "pytest",
    ],
    project_urls={
        "Issues": "https://github.com/Fxe/pyeutils/issues",
    },
)
