# Copyright (c) 2022, 2023, Panagiotis Tsirigotis

# This file is part of linuxnet-iptables.
#
# linuxnet-iptables is free software: you can redistribute it and/or
# modify it under the terms of version 3 of the GNU Affero General Public
# License as published by the Free Software Foundation.
#
# linuxnet-iptables is distributed in the hope that it will be useful, but
# WITHOUT ANY WARRANTY; without even the implied warranty of MERCHANTABILITY
# or FITNESS FOR A PARTICULAR PURPOSE. See the GNU Affero General Public
# License for more details.
#
# You should have received a copy of the GNU Affero General
# Public License along with linuxnet-iptables. If not, see
# <https://www.gnu.org/licenses/>.

import setuptools.command.build
import os
import setuptools


from os.path import abspath, dirname

NAME = "linuxnet-iptables"

#
# Check if a suitable Sphinx version is available
#
sphinx_is_available = False

try:
    from sphinx import __version__ as sphinx_version
    sphinx_is_available = True
except ImportError:
    print("** WARNING: sphinx is not available; will not build manpages")

if sphinx_is_available:
    vers = sphinx_version.split('.')
    if (int(vers[0]), int(vers[1])) < (4, 4):
        sphinx_is_available = False
        print(f"** WARNING: need sphinx 4.4 or later; found {sphinx_version}")


class LinuxnetIptablesBuild(setuptools.command.build.build):
    """Custom build command that also builds the Sphinx documentation.
    """

    def have_sphinx(self) -> bool:
        return sphinx_is_available

    setuptools.command.build.build.sub_commands.append(
                                        ('build_sphinx', have_sphinx))


def read_version():
    """Returns the value of the _version_ variable from the
    metadata.py module
    """
    source_dir = NAME.replace('-', '/')
    path = os.path.join(source_dir, 'metadata.py')
    globs = {'__builtins__':{}}
    mdvars = {}
    with open(path, encoding='utf-8') as f:
        exec(f.read(), globs, mdvars)
    return mdvars['_version_']

delim = "-----------------"

print(f"{delim} BEGIN {NAME} {delim}")

setup_args = {}

if sphinx_is_available:
    from sphinx.setup_command import BuildDoc
    setup_args['cmdclass'] = {
                                'build_sphinx': BuildDoc,
                                'build' : LinuxnetIptablesBuild,
                            }
    html_destdir = f'share/doc/{NAME}/html'
    htmldir = 'build/sphinx/html'
    setup_args['data_files'] = [
            (
                'share/man/man3',
                    [
                        'build/sphinx/man/man3/linuxnet.iptables.3',
                    ]
            ),
            (
                html_destdir,
                    [
                        f'{htmldir}/index.html',
                        f'{htmldir}/iptables_api.html',
                        f'{htmldir}/genindex.html',
                        f'{htmldir}/py-modindex.html',
                        f'{htmldir}/search.html',
                        f'{htmldir}/.buildinfo',
                        f'{htmldir}/searchindex.js',
                        f'{htmldir}/objects.inv',
                    ]
            ),
            (
                f'{html_destdir}/_static',
                    [
                        f'{htmldir}/_static/pygments.css',
                        f'{htmldir}/_static/basic.css',
                        f'{htmldir}/_static/doctools.js',
                        f'{htmldir}/_static/documentation_options.js',
                        f'{htmldir}/_static/file.png',
                        f'{htmldir}/_static/jquery-3.5.1.js',
                        f'{htmldir}/_static/jquery.js',
                        f'{htmldir}/_static/language_data.js',
                        f'{htmldir}/_static/minus.png',
                        f'{htmldir}/_static/plus.png',
                        f'{htmldir}/_static/searchtools.js',
                        f'{htmldir}/_static/underscore-1.13.1.js',
                        f'{htmldir}/_static/underscore.js',
                        f'{htmldir}/_static/alabaster.css',
                        f'{htmldir}/_static/custom.css',
                    ]
            ),
            (
                f'{html_destdir}/_sources',
                    [
                        f'{htmldir}/_sources/index.rst.txt',
                        f'{htmldir}/_sources/iptables_api.rst.txt',
                    ]
            ),
            (
                f'{html_destdir}/_modules',
                    [
                        f'{htmldir}/_modules/index.html',
                    ]
            ),
            (
                f'{html_destdir}/_modules/linuxnet/iptables',
                    [
                        f'{htmldir}/_modules/linuxnet/iptables/chain.html',
                        f'{htmldir}/_modules/linuxnet/iptables/exceptions.html',
                        f'{htmldir}/_modules/linuxnet/iptables/match.html',
                        f'{htmldir}/_modules/linuxnet/iptables/rule.html',
                        f'{htmldir}/_modules/linuxnet/iptables/table.html',
                        f'{htmldir}/_modules/linuxnet/iptables/target.html',
                    ]
            ),
        ]
    setup_args['options'] = { 'build_sphinx' : { 'builder' : 'man html' } }

with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

setuptools.setup(
    name=NAME,
    version=read_version(),
    author="Panagiotis (Panos) Tsirigotis",
    author_email="ptsirigotis01@gmail.com",
    url="https://gitlab.com/panos-tools/linuxnet-iptables",
    project_urls={
            'Source': "https://gitlab.com/panos-tools/linuxnet-iptables",
            'Documentation': "https://linuxnet-iptables.readthedocs.io/en/latest/index.html",
        },
    description="programmatic access to Linux iptables",
    license="AGPLv3",
    long_description=long_description,
    long_description_content_type="text/markdown",
    packages=[
        'linuxnet',
        'linuxnet.iptables',
        'linuxnet.iptables.matches',
        'linuxnet.iptables.targets',
        ],
    classifiers=[       # From: https://pypi.org/classifiers/
        "Development Status :: 5 - Production/Stable",
        "Intended Audience :: Developers",
        "License :: OSI Approved :: GNU Affero General Public License v3",
        "Operating System :: POSIX :: Linux",
        "Programming Language :: Python :: 3 :: Only",
        "Topic :: Software Development :: Libraries",
        "Topic :: System :: Networking :: Firewalls"
    ],
    python_requires='>=3.6',
    test_suite="tests",
    **setup_args
)

print(f"{delim} END {NAME} {delim}")
