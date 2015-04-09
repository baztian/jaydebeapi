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
        self.conn = jaydebeapi.connect('org.jaydebeapi.mockdriver.MockDriver',
                                       'jdbc:jaydebeapi://dummyurl')

    def tearDown(self):
        self.conn.close()

    def test_all_db_api_type_objects_have_valid_mapping(self):
        extra_type_mappings = { 'DATE': 'getDate',
                                'TIME': 'getTime',
                                'TIMESTAMP': 'getTimestamp' }
        for db_api_type in jaydebeapi.__dict__.values():
            if isinstance(db_api_type, jaydebeapi.DBAPITypeObject):
                for jsql_type_name in db_api_type.values:
                    self.conn.jconn.mockType(jsql_type_name)
                    cursor = self.conn.cursor()
                    cursor.execute("dummy stmt")
                    cursor.fetchone()
                    verify = self.conn.jconn.verifyResultSet()
                    verify_get = getattr(verify,
                                         extra_type_mappings.get(jsql_type_name,
                                                                 'getObject'))
                    verify_get(1)

    def test_exception_on_execute(self):
        dummy_msg = "expected"
        self.conn.jconn.mockExceptionOnExecute(dummy_msg)
        cursor = self.conn.cursor()
        try:
            cursor.execute("dummy stmt")
            fail("expected exception")
        except jaydebeapi.Error, e:
            self.assertEquals(str(e), 'expected')
