# -*- coding: utf-8 -*-
import os
import re

import pip
from setuptools import find_packages, setup

here = os.path.abspath(os.path.dirname(__file__))

try:
    prod_requirements = pip.req.parse_requirements('requirements.txt')
except:
    # new versions of pip requires a session
    prod_requirements = pip.req.parse_requirements(
        'requirements.txt', session=pip.download.PipSession())

try:
    test_requirements = pip.req.parse_requirements('requirements.txt')
except:
    # new versions of pip requires a session
    test_requirements = pip.req.parse_requirements(
        'requirements.txt', session=pip.download.PipSession())

try:
    dev_requirements = pip.req.parse_requirements('requirements.txt')
except:
    # new versions of pip requires a session
    dev_requirements = pip.req.parse_requirements(
        'requirements.txt', session=pip.download.PipSession())

try:
    doc_requirements = pip.req.parse_requirements('requirements.txt')
except:
    # new versions of pip requires a session
    doc_requirements = pip.req.parse_requirements(
        'requirements.txt', session=pip.download.PipSession())


def find_version(*file_paths):
    '''
    see https://github.com/pypa/sampleproject/blob/master/setup.py
    '''

    with open(os.path.join(here, *file_paths), 'r') as f:
        version_file = f.read()

    # The version line must have the form
    # __version__ = 'ver'
    version_match = re.search(r"^__version__ = ['\"]([^'\"]*)['\"]",
                              version_file, re.M)
    if version_match:
        return version_match.group(1)
    raise RuntimeError('Unable to find version string. '
                       'Should be at the first line of __init__.py.')


setup(
    name='sonopluie',
    version=find_version('sonopluie', '__init__.py'),
    description='Ballade sonore en parapluie géolocalisé.',
    url='https://github.com/akken44/sonopluie',
    author='dev',
    author_email='akken@abacadis.fr',
    license='GPLv3',
    classifiers=[
        'Development Status :: 3 - Alpha',
        'Intended Audience :: Developers',
        'Programming Language :: Python :: 3.4',
        'Programming Language :: Python :: 3.5',
    ],
    packages=find_packages(),
    # install_requires={prod_requirements},
    test_suite='tests',
    extras_require={
        # 'test': test_requirements,
        # 'dev': dev_requirements,
        # 'prod': prod_requirements,
        # 'doc': doc_requirements
    }
)
