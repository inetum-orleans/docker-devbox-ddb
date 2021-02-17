#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import io
import os
import re
import sys

from setuptools import setup, find_packages

try:
    from semantic_release import setup_hook

    setup_hook(sys.argv)
except ImportError:
    pass

here = os.path.abspath(os.path.dirname(__file__))

with io.open(os.path.join(here, 'README.md'), encoding='utf-8') as f:
    readme = f.read()

with io.open(os.path.join(here, 'CHANGELOG.md'), encoding='utf-8') as f:
    history = f.read()

project_dir = os.path.dirname(os.path.realpath(__file__))

install_requires = [
    "colorama",
    "colorlog",
    "verboselogs",
    "netifaces",
    "requests",
    "PyYAML",
    "marshmallow",
    "dotty-dict",
    "deepmerge",
    "diskcache",
    "python-slugify",
    "dictdiffer",
    "Jinja2",
    "braceexpand",
    "toposort",
    "cookiecutter",
    "jsonnet-binary",
    "zgitignore",
    "cached-property",
    "docker[tls]",  # Because newer version makes communication fails with current docker registry
    "dockerfile-parse",
    "cfssl>=0.0.3b243",
    "cryptography",
    "watchdog",
    "gitpython",
    "chmod-monkey>=1.1.1",
    "paramiko",
    "wcmatch",
    "marshmallow-union",
    "progress",
    "ordered-set",
    "patch",
    "semver",
    "distro"
]

dev_requires = [
    "python-semantic-release",
    "pyinstaller",
    "commitizen",
    "pre-commit",
    "tox",
    "pylint>=2.6.2",
    "docker-compose",
    "pytest",
    "coverage",
    "docker-compose",
    "waiting",
    "pytest-mock",
    "pytest-cov",
    "pex"
]

package_data = []

entry_points = {
    'console_scripts': [
        'ddb = ddb.__main__:console_script'
    ],
    "pytest11": [
        "docker_compose=tests.pytest_docker_compose:plugin",
    ],
}

with io.open('ddb/__version__.py', 'r') as f:
    version = re.search(r'^__version__\st*=\s*[\'"]([^\'"]*)[\'"]$', f.read(), re.MULTILINE).group(1)

args = dict(name='docker-devbox-ddb',
            version=version,
            description='ddb - Erase environment differences, make developers happy !',
            long_description=readme + '\n' * 2 + history,
            long_description_content_type='text/markdown',
            # Get strings from http://pypi.python.org/pypi?%3Aaction=list_classifiers
            classifiers=['Development Status :: 5 - Production/Stable',
                         'License :: OSI Approved :: MIT License',
                         'Operating System :: OS Independent',
                         'Intended Audience :: Developers',
                         'Programming Language :: Python :: 3',
                         'Programming Language :: Python :: 3.6',
                         'Programming Language :: Python :: 3.7',
                         'Programming Language :: Python :: 3.8',
                         'Programming Language :: Python :: 3.9',
                         'Topic :: Software Development :: Libraries :: Python Modules'
                         ],
            keywords='docker docker-compose development environment devops templates jsonnet jinja watch',
            author='Rémi Alvergnat',
            author_email='remi.alvergnat@gfi.world',
            url='https://github.com/inetum-orleans/docker-devbox-ddb',
            download_url='https://pypi.python.org/packages/source/g/docker-devbox-ddb/docker-devbox-ddb-%s.tar.gz' % version,
            license='MIT',
            packages=find_packages(),
            include_package_data=True,
            install_requires=install_requires,
            entry_points=entry_points,
            zip_safe=True,
            extras_require={
                'dev': dev_requires
            })

setup(**args)
