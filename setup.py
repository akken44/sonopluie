# -*- coding: utf-8 -*-
import os
import re
from setuptools import setup, find_packages

here = os.path.abspath(os.path.dirname(__file__))


requirements = (
)

dev_requirements = (
)

doc_requirements = (
)

prod_requirements = (
)


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
    install_requires=requirements,
    test_suite='tests',
    extras_require={
        'dev': dev_requirements,
        'prod': prod_requirements,
        'doc': doc_requirements
    }
)
