"""
"""

from setuptools import setup, find_packages
from codecs import open
from os import path

here = path.abspath(path.dirname(__file__))

with open(path.join(here, 'README.md'), encoding='utf-8') as f:
    long_description = f.read()

setup(
    name='FaroresWind',

    # Versions should comply with PEP440.  For a discussion on single-sourcing
    # the version across setup.py and the project code, see
    # https://packaging.python.org/en/latest/single_source_version.html
    version='0.5.0',

    description='Electronic nose',
    long_description=long_description,

    # The project's main homepage.
    url='https://github.com/VandroiyLabs/FaroresWind',

    # Author details
    author='',
    author_email='',

    license='GPL-3.0',

    # See https://pypi.python.org/pypi?%3Aaction=list_classifiers
    classifiers=[
        'Development Status :: 3 - Alpha',
        'Intended Audience :: Recordings from electronic nose',
        'Topic :: Data analysis :: Electronic nose :: Sensors ',

        'License :: GPL-3.0',

        'Programming Language :: Python :: 2',
        'Programming Language :: Python :: 2.6',
        'Programming Language :: Python :: 2.7',
    ],

    keywords='electronic nose, sensors, MOX',

    packages=[  'faroreswind.collector',
                'faroreswind.server',
                'faroreswind.client'
                ],

    install_requires=[],


    extras_require={},
    package_data={},

)
