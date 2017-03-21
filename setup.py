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

install_requires = []
if not sys.platform.lower().startswith('java'):
    install_requires.append('JPype1')

setup(
    #basic package data
    name = 'JayDeBeApi',
    version = '1.1.1',
    author = 'Bastian Bowe',
    author_email = 'bastian.dev@gmail.com',
    license = 'GNU LGPL',
    url='https://github.com/baztian/jaydebeapi',
    description=('Use JDBC database drivers from Python 2/3 or Jython with a DB-API.'),
    long_description=open('README.rst').read(),
    keywords = ('db api java jdbc bridge connect sql jpype jython'),
    classifiers = [
        'Development Status :: 4 - Beta',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: GNU Library or Lesser General Public License (LGPL)',
        'Programming Language :: Java',
        'Programming Language :: Python',
        'Programming Language :: Python :: 2',
        'Programming Language :: Python :: 3',
        'Topic :: Database',
        'Topic :: Software Development :: Libraries :: Java Libraries',
        'Topic :: Software Development :: Libraries :: Python Modules',
        ],

    packages=['jaydebeapi'],
    install_requires=install_requires,
    )
