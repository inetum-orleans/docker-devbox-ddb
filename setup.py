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

def handle_requirements(*requirements_filepaths):
    dependency_link_pattern = re.compile("(\S+:\/\/\S+)#egg=(\S+)")
    dependency_links = []
    requires = []

    for requirements_filepath in requirements_filepaths:
        with open(requirements_filepath) as f:
            requirements_lines = list(map(str.strip, f.read().splitlines()))

        requires_item = []
        for requirement_line in requirements_lines:
            if not requirement_line or requirement_line.startswith('-') or requirement_line.startswith('#'):
                continue
            match = dependency_link_pattern.match(requirement_line)
            if match:
                requires_item.append(match.group(2))
                dependency_links.append(match.group(1))
            else:
                requires_item.append(requirement_line)
        requires.append(requires_item)

    return requires[0] if len(requires) == 1 else tuple(requires), dependency_links

(install_requires, dev_requires), dependency_links = \
    handle_requirements('requirements.txt', 'requirements-dev.txt')

print(dev_requires)

package_data = []

entry_points = {
    'console_scripts': [
        'ddb = ddb.__main__:console_script'
    ]
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
            dependency_links=dependency_links,
            entry_points=entry_points,
            zip_safe=True,
            extras_require={
                'dev': dev_requires
            })

setup(**args)
