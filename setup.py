#!/usr/bin/env python

import os
import setuptools

import raildriver


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
    version='.'.join(str(v) for v in raildriver.VERSION),
    description='Python interface to Train Simulator\'s raildriver.dll',
    long_description=open(os.path.join(os.path.dirname(__file__), 'README.rst')).read(),
    url='https://github.com/centralniak/py-raildriver',
    license='MIT License',
    platforms=['Windows'],
    classifiers=CLASSIFIERS,
    install_requires=[
    ],
    tests_require=open('test_requirements.txt').read(),
    packages=setuptools.find_packages(),
    # package_data={'raildriver': package_data},
    include_package_data=False,
    zip_safe=False,
    test_suite='nose.collector',
)
