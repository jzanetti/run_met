#!/usr/bin/env python

""" Setup for run_met """

from glob import glob
from setuptools import find_packages, setup
from os.path import basename, dirname, realpath

def main():
    return setup(
        author='Forecasting Research group',
        author_email='research@metservice.com',
        data_files=[('run_met/etc', glob('etc/*'))],
        description='to be added',
        maintainer='Forecasting Research group',
        maintainer_email='research@metservice.com',
        # Use name of the directory as name
        name=basename(dirname(realpath(__file__))),
        scripts=['scripts/run_met.py'],
        packages=find_packages(),
        zip_safe=False
    )

if __name__ == '__main__':
    main()
