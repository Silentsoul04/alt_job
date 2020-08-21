#! /usr/bin/env python3

from setuptools import setup
import sys
if sys.version_info[0] < 3: 
    raise EnvironmentError("Sorry, you must use Python 3")
import pathlib


# The directory containing this file
HERE = pathlib.Path(__file__).parent

#Version of the project
version = {}
exec((HERE / "alt_job" / "__version__.py").read_text(), version)

# The text of the README file
README = (HERE / "README.md").read_text()

setup(
    name='alt_job',
    description="Atl Job scrapes a bunch of green/social/alternative websites to send digest of new job posting by email.",
    url='https://github.com/tristanlatr/alt_job',
    maintainer='tristanlatr',
    version=version['__version__'],
    packages=['alt_job',],
    install_requires=[
          'scrapy', 'bs4', 'XlsxWriter', 'scrapy-user-agents'
    ],
    classifiers=[
        "Programming Language :: Python :: 3",
    ],
    license='The MIT License',
    long_description=README,
    long_description_content_type="text/markdown"
)