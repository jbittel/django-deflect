#!/usr/bin/env python

from distutils.core import setup

from deflect import __version__ as version


packages = [
    'deflect',
    'deflect.tests',
]

package_data = {
    '': ['LICENSE', 'README.rst'],
}

with open('README.rst') as f:
    readme = f.read()

setup(
    name='django-deflect',
    version=version,
    description='A Django short URL redirection application',
    long_description=readme,
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
    install_requires=[
        'base32-crockford == 0.1.0',
        'qrcode == 4.0.1',
        'requests == 2.0.0',
    ],
)
