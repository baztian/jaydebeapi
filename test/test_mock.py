#-*- coding: utf-8 -*-

# Copyright 2015 Bastian Bowe
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

import jaydebeapi

import unittest2 as unittest

class MockTest(unittest.TestCase):

    def setUp(self):
        self.conn = jaydebeapi.connect('org.jaydebeapi.mockdriver.MockDriver', 'jdbc:jaydebeapi://dummyurl')

    def tearDown(self):
        self.conn.close()

    def test_execute(self):
        cursor = self.conn.cursor()
        cursor.execute("dummy stmt")
