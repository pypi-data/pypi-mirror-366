#!/usr/bin/env python
import sys
from admin_honeypot import __version__, __description__, __license__

try:
    from setuptools import setup, find_packages
except ImportError:
    from distutils.core import setup, find_packages

setup(
    name='django-honeypot-admin',
    version=__version__,
    description=__description__,
    long_description=open('./README.rst', 'r').read(),
    classifiers=[
        'Development Status :: 5 - Production/Stable',
        'Framework :: Django',
        'Framework :: Django :: 3.2',
        'Framework :: Django :: 4.0',
        'Framework :: Django :: 4.1',
        'Framework :: Django :: 4.2',
        'Framework :: Django :: 5.0',
        'Framework :: Django :: 5.1',
        'Framework :: Django :: 5.2',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: MIT License',
        'Natural Language :: English',
        'Operating System :: OS Independent',
        'Programming Language :: Python',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.8',
        'Programming Language :: Python :: 3.9',
        'Programming Language :: Python :: 3.10',
        'Programming Language :: Python :: 3.11',
        'Programming Language :: Python :: 3.12',
        'Topic :: Internet :: WWW/HTTP :: Dynamic Content',
        ],
    keywords='django admin honeypot trap security',
    author='Derek Payton',
    author_email='derek.payton@gmail.com',
    maintainer='Vignesh (Alien501)',
    maintainer_email='cvignesh404@gmail.com',
    url='https://github.com/Alien501/django-admin-honeypot',
    download_url='https://github.com/Alien501/django-admin-honeypot/tarball/v%s' % __version__,
    license=__license__,
    include_package_data=True,
    packages=find_packages(),
    zip_safe=False,
    install_requires=[
        'django>=3.2',
        'django-ipware',
    ]
)
