#!/usr/bin/env python
from ez_setup import use_setuptools
use_setuptools()

from setuptools import setup, find_packages

def read(fname):
    return open(os.path.join(os.path.dirname(__file__), fname)).read()

setup(
    name = 'riskiq',
    version = '0.1',
    description = 'client for RiskIQ REST API',
    keywords = 'riskiq API REST',
    packages = find_packages(),
    install_requires = ['requests'],
    long_description=read('README.md'),
    classifiers=[
        'Development Status :: 3 - Alpha',
        #'Development Status :: 4 - Beta',
        #'Development Status :: 5 - Production/Stable',
        #'Development Status :: 6 - Mature',
    ],
    entry_points = {
        'console_scripts': [
            'riq-pdns = riskiq.cli.pdns:main',
            'riq-config = riskiq.cli.config:main',
            'riq-blacklist = riskiq.cli.blacklist:main',
        ],
    },
)
