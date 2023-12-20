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

from setuptools import setup

install_requires = [
    'JPype1>=1.0.0',
    'pyarrow>=12.0.0',
]

package_name = 'JayDeBeApiArrow'

setup(
    # basic package data
    name=package_name,
    version='0.0.1-a1',
    author='HenryNebula',
    author_email='henrynebula0710@gmail.com',
    license='GNU LGPL',
    url='https://github.com/HenryNebula/jaydebeapiarrow.git',
    description='Use JDBC database drivers from Python 3 with a DB-API, accelerated with Apache Arrow.',
    long_description=open('README.rst').read(),
    keywords = ('db api java jdbc bridge connect sql jpype apache-arrow'),
    classifiers = [
        'Development Status :: 3 - Alpha',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: GNU Library or Lesser General Public License (LGPL)',
        'Programming Language :: Java',
        'Programming Language :: Python',
        'Programming Language :: Python :: 3',
        'Topic :: Database',
        'Topic :: Software Development :: Libraries :: Java Libraries',
        'Topic :: Software Development :: Libraries :: Python Modules',
        ],
    packages=[ package_name.lower(), package_name.lower() + ".lib"],
    install_requires=install_requires,
    include_package_data=True,
    python_requires='>=3.8',
)
