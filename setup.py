#!/usr/bin/env python

from setuptools import find_packages
from setuptools import setup

from deflect import __version__ as version


with open('README.rst') as f:
    readme = f.read()

setup(
    name='django-deflect',
    version=version,
    description='A Django short URL redirection application',
    long_description=readme,
    license='BSD',
    author='Jason Bittel',
    author_email='jason.bittel@gmail.com',
    url='https://github.com/jbittel/django-deflect',
    download_url='https://github.com/jbittel/django-deflect/downloads',
    packages=find_packages(),
    include_package_data=True,
    install_requires=[
        'base32-crockford',
        'qrcode',
        'requests',
    ],
    classifiers=[
        'Development Status :: 3 - Alpha',
        'Environment :: Web Environment',
        'Programming Language :: Python',
        'Programming Language :: Python :: 2',
        'Programming Language :: Python :: 2.7',
        'Framework :: Django',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: BSD License',
        'Operating System :: OS Independent',
        'Topic :: Software Development :: Libraries :: Python Modules',
    ],
    keywords=['django', 'url', 'short url', 'redirect', 'redirection'],
)
