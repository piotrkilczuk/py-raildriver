#!/usr/bin/env python

import os
import setuptools


CLASSIFIERS = [
    'Development Status :: 5 - Production/Stable',
    'Intended Audience :: Developers',
    'License :: OSI Approved :: MIT License',
    'Operating System :: Microsoft :: Windows',
    'Programming Language :: Python',
    'Topic :: Software Development :: Libraries',
]


setuptools.setup(
    author='Piotr Kilczuk',
    author_email='piotr@tymaszweb.pl',
    name='py-raildriver',
    version='1.1.7',
    description='Python interface to Train Simulator 2016',
    long_description=open(os.path.join(os.path.dirname(__file__), 'README.rst')).read(),
    url='https://github.com/centralniak/py-raildriver',
    license='MIT License',
    platforms=['Windows'],
    classifiers=CLASSIFIERS,
    install_requires=open('requirements.txt').read(),
    tests_require=open('test_requirements.txt').read(),
    packages=setuptools.find_packages(),
    include_package_data=False,
    zip_safe=False,
    test_suite='nose.collector',
)
