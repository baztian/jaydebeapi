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

import ez_setup
ez_setup.use_setuptools()
from setuptools import setup, find_packages

print find_packages('src')
setup(
    #basic package data
    name = 'JayDeBeApi',
    version = '0.1.3',
    author = 'Bastian Bowe',
    author_email = 'bastian.bowe@gmail.com',
    license = 'GNU LGPL',
    url='https://launchpad.net/jaydebeapi',
    description=('A bridge from JDBC database drivers to Python DB-API.'),
    long_description=file('README.rst').read(),
    keywords = ('db api java jdbc bridge connect sql jpype jython'),
    classifiers = [
        'Development Status :: 3 - Alpha',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: GNU Library or Lesser General Public License (LGPL)',
        'Programming Language :: Java',
        'Programming Language :: Python',
        'Programming Language :: Python :: 2',
        'Topic :: Database',
        'Topic :: Software Development :: Libraries :: Java Libraries',
        'Topic :: Software Development :: Libraries :: Python Modules',
        ],

    packages=find_packages('src'),
    package_dir={ '': 'src' },
    )
