#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import io
import os
import re

from setuptools import setup, find_packages

here = os.path.abspath(os.path.dirname(__file__))

with io.open(os.path.join(here, 'README.md'), encoding='utf-8') as f:
    readme = f.read()

dependency_links = []

install_requires = ['vyper-config>=0.5', 'colorama', 'netifaces', 'requests', 'PyYAML']

dev_require = ['zest.releaser[recommended]', 'tox', 'pylint', 'pytest']

package_data = []

entry_points = {
    'console_scripts': [
        'ddb = ddb.__main__:main'
    ],
    'ddb_features': [
        'copy = ddb.feature.copy:CopyFeature',
        'core = ddb.feature.core:CoreFeature',
        'docker = ddb.feature.docker:DockerFeature',
        'gitignore = ddb.feature.gitignore:GitignoreFeature',
        'jinja = ddb.feature.jinja:JinjaFeature',
        'jsonnet = ddb.feature.jsonnet:JsonnetFeature',
        'plugins = ddb.feature.plugins:PluginsFeature',
        'shell = ddb.feature.shell:ShellFeature',
        'symlinks = ddb.feature.symlinks:SymlinksFeature',
        'ytt = ddb.feature.ytt:YttFeature'
    ]
}

with io.open('ddb/__version__.py', 'r') as f:
    version = re.search(r'^__version__\st*=\s*[\'"]([^\'"]*)[\'"]$', f.read(), re.MULTILINE).group(1)

args = dict(name='ddb',
            version=version,
            description='ddb - Does the magic inside Docker Devbox',
            long_description=readme,
            long_description_content_type='text/markdown',
            # Get strings from http://pypi.python.org/pypi?%3Aaction=list_classifiers
            classifiers=['Development Status :: 2 - Pre-Alpha',
                         'License :: OSI Approved :: MIT License',
                         'Operating System :: OS Independent',
                         'Intended Audience :: Developers',
                         'Programming Language :: Python :: 3',
                         'Programming Language :: Python :: 3.5',
                         'Programming Language :: Python :: 3.6',
                         'Programming Language :: Python :: 3.7',
                         'Programming Language :: Python :: 3.8',
                         'Topic :: Multimedia',
                         'Topic :: Software Development :: Libraries :: Python Modules'
                         ],
            keywords='docker docker-compose development environment devops',
            author='Rémi Alvergnat',
            author_email='remi.alvergnat@gfi.fr',
            url='https://github.com/gfi-centre-ouest/docker-devbox-ddb',
            download_url='https://pypi.python.org/packages/source/g/ddb/ddb-%s.tar.gz' % version,
            license='MIT',
            packages=find_packages(),
            package_data={},
            include_package_data=True,
            install_requires=install_requires,
            dependency_links=dependency_links,
            entry_points=entry_points,
            zip_safe=True,
            extras_require={
                'dev': dev_require
            })

setup(**args)
