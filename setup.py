#!/usr/bin/env python

from distutils.core import setup
import os

from deflect import __version__ as version


def read_file(filename):
    """
    Utility function to read a provided filename.
    """
    return open(os.path.join(os.path.dirname(__file__), filename)).read()


packages = [
    'deflect',
    'deflect.tests',
]

package_data = {
    '': ['LICENSE', 'README.rst'],
}

setup(
    name='django-deflect',
    version=version,
    description='A Django short URL redirection application',
    long_description=read_file('README.rst'),
    author='Jason Bittel',
    author_email='jason.bittel@gmail.com',
    url='https://github.com/jbittel/django-deflect',
    download_url='https://github.com/jbittel/django-deflect/downloads',
    package_dir={'deflect': 'deflect'},
    packages=packages,
    package_data=package_data,
    license='BSD',
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
