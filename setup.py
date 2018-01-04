#!/usr/bin/env python

""" Setup for run_met """

from distutils.core import setup
from glob import glob
import os

VERSION_FILE = './run_met/_version.py'
if not os.path.exists(VERSION_FILE):
    raise RuntimeError('Version file: %s  does not exist' % VERSION_FILE)
execfile(VERSION_FILE)
if not '__version__' in dir():
    raise RuntimeError('Version file: %s  does not supply __version__')

def main():
    return setup(
        author='Forecasting Research group',
        author_email='research@metservice.com',
        data_files=[('run_met/etc', glob('etc/*'))],
        description='to be added',
        maintainer='Forecasting Research group',
        maintainer_email='research@metservice.com',
        name='run_met',
        version=__version__,
        scripts=['scripts/start_met.py', 'scripts/start_multiple_met.py', 'scripts/start_plot.py'],
        packages=['run_met'],
        zip_safe=False,
        ext_modules=[],
        ext_package='run_met'
    )

if __name__ == '__main__':
    main()
