#!/usr/bin/env python
"""proxenos: A rendezvous hashing and service routing toolkit."""
from __future__ import absolute_import

import io
import sys

import setuptools


__all__ = ('setup',)


def readme():
    try:
        with io.open('README.rst') as fp:
            return fp.read()
    except OSError:
        return ''


def setup():
    """Package setup entrypoint."""
    extra_requirements = {
        ':python_version=="2.7"': ['enum34'],
        ':python_version<"3.5"': ['typing'],
        'consul': ['consulate'],
        'murmur': ['mmh3'],
    }
    install_requirements = [
        'attrs',
        'consulate',
        'netaddr',
        'siphash',
        'stevedore',
    ]
    setup_requirements = ['six', 'setuptools>=17.1', 'setuptools_scm']
    needs_sphinx = {
        'build_sphinx',
        'docs',
        'upload_docs',
    }.intersection(sys.argv)
    if needs_sphinx:
        setup_requirements.append('sphinx')
    setuptools.setup(
        author='David Gidwani',
        author_email='david.gidwani@gmail.com',
        classifiers=[
            'Development Status :: 2 - Pre-Alpha',
            'Environment :: Console',
            'Intended Audience :: Developers',
            'License :: OSI Approved :: MIT License',
            'Operating System :: MacOS',
            'Operating System :: Microsoft :: Windows',
            'Operating System :: POSIX :: Linux',
            'Operating System :: Unix',
            'Programming Language :: Python :: 2',
            'Programming Language :: Python :: 2.7',
            'Programming Language :: Python :: 3',
            'Programming Language :: Python :: 3.3',
            'Programming Language :: Python :: 3.4',
            'Programming Language :: Python :: 3.5',
            'Programming Language :: Python :: 3.6',
            'Programming Language :: Python :: Implementation :: CPython',
            'Programming Language :: Python :: Implementation :: PyPy',
            'Programming Language :: Python',
            'Topic :: Software Development :: Libraries :: Python Modules',
            'Topic :: Software Development :: Libraries',
            'Topic :: Utilities',
        ],
        description=__doc__,
        entry_points={
            'console_scripts': [
                'proxenos = proxenos.cli:main',
            ],
            'proxenos.mapper': [
                'consul = proxenos.mappers.consul'
                ':ConsulClusterMapper [consul]',
            ],
        },
        extras_require=extra_requirements,
        include_package_data=True,
        install_requires=install_requirements,
        long_description=readme(),
        name='proxenos',
        package_dir={'': 'src'},
        packages=setuptools.find_packages('./src'),
        setup_requires=setup_requirements,
        url='https://github.com/darvid/proxenos',
        use_scm_version=True,
        zip_safe=False,
    )


if __name__ == '__main__':
    setup()
