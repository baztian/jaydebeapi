# Copyright 2010 Bastian Bowe
#
# This file is part of JayDeBeApi.
# JayDeBeApi is free software: you can redistribute it and/or modify
# it under the terms of the GNU Lesser General Public License as
# published by the Free Software Foundation, either version 3 of the
# License, or (at your option) any later version.
# 
# JayDeBeApi is distributed in the hope that it will be useful, but
# WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the GNU
# Lesser General Public License for more details.
# 
# You should have received a copy of the GNU Lesser General Public
# License along with JayDeBeApi.  If not, see
# <http://www.gnu.org/licenses/>.
# 

import sys

from setuptools import setup

install_requires = [ 'JPype1 ; python_version > "2.7" and platform_python_implementation != "Jython"',]

setup(
    #basic package data
    name = 'JayDeBeApiArrow',
    version = '0.0.1',
    author = 'HenryNebula',
    author_email = 'henrynebula0710@gmail.com',
    license = 'GNU LGPL',
    url='https://github.com/HenryNebula/jaydebeapiArrow.git',
    description=('Use JDBC database drivers from Python 3 with a DB-API and Apache Arrow for acceleration.'),
    long_description=open('README.rst').read(),
    keywords = ('db api java jdbc bridge connect sql jpype arrow'),
    classifiers = [
        'Development Status :: 4 - Beta',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: GNU Library or Lesser General Public License (LGPL)',
        'Programming Language :: Java',
        'Programming Language :: Python',
        'Programming Language :: Python :: 3',
        'Topic :: Database',
        'Topic :: Software Development :: Libraries :: Java Libraries',
        'Topic :: Software Development :: Libraries :: Python Modules',
        ],

    packages=['jaydebeapiarrow'],
    install_requires=install_requires,
    )
