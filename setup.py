#!/usr/bin/env python

VERSION="0.1.1"

DESCRIPTION = "Generates maps from EuroStat data"

def main():
    import io
    import os
    from setuptools import setup

    with io.open('README.rst', encoding="utf8") as fp:
        long_description = fp.read().strip()

    with open('requirements.txt') as f:
        required = f.read().splitlines()

    classifiers=[
        "Programming Language :: Python :: 2",
        "Programming Language :: Python :: 2.7",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.3",
        "Programming Language :: Python :: 3.4",
        "Programming Language :: Python :: 3.5",
    ]

    setup_params = dict(
        name="MapViz",
        version=VERSION,
        description=DESCRIPTION,
        long_description=long_description,
        url="https://github.com/laszukdawid/MapViz",
        author="Dawid Laszuk",
        author_email="laszukdawid@gmail.com",
        classifiers=classifiers,
        keywords="maps visualisation eurostat nuts",
        packages=["MapViz"],
        install_requires=required
    )

    dist = setup(**setup_params)

if __name__=="__main__":
    main()
