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

try:
    import unittest2 as unittest
except ImportError:
    import unittest

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
                    with self.conn.cursor() as cursor:
                        cursor.execute("dummy stmt")
                        cursor.fetchone()
                    verify = self.conn.jconn.verifyResultSet()
                    verify_get = getattr(verify,
                                         extra_type_mappings.get(jsql_type_name,
                                                                 'getObject'))
                    verify_get(1)

    def test_ancient_date_mapped(self):
        self.conn.jconn.mockDateResult(1899, 12, 31)
        with self.conn.cursor() as cursor:
            cursor.execute("dummy stmt")
            result = cursor.fetchone()
        self.assertEquals(result[0], "1899-12-31")

    def test_decimal_scale_zero(self):
        self.conn.jconn.mockBigDecimalResult(12345, 0)
        with self.conn.cursor() as cursor:
            cursor.execute("dummy stmt")
            result = cursor.fetchone()
        self.assertEquals(str(result[0]), "12345")

    def test_decimal_places(self):
        self.conn.jconn.mockBigDecimalResult(12345, 1)
        with self.conn.cursor() as cursor:
            cursor.execute("dummy stmt")
            result = cursor.fetchone()
        self.assertEquals(str(result[0]), "1234.5")

    def test_double_decimal(self):
        self.conn.jconn.mockDoubleDecimalResult(1234.5)
        with self.conn.cursor() as cursor:
            cursor.execute("dummy stmt")
            result = cursor.fetchone()
        self.assertEquals(str(result[0]), "1234.5")

    def test_sql_exception_on_execute(self):
        self.conn.jconn.mockExceptionOnExecute("java.sql.SQLException", "expected")
        with self.conn.cursor() as cursor:
            try:
                cursor.execute("dummy stmt")
                self.fail("expected exception")
            except jaydebeapi.DatabaseError as e:
                self.assertEquals(str(e), "java.sql.SQLException: expected")

    def test_runtime_exception_on_execute(self):
        self.conn.jconn.mockExceptionOnExecute("java.lang.RuntimeException", "expected")
        with self.conn.cursor() as cursor:
            try:
                cursor.execute("dummy stmt")
                self.fail("expected exception")
            except jaydebeapi.InterfaceError as e:
                self.assertEquals(str(e), "java.lang.RuntimeException: expected")

    def test_sql_exception_on_commit(self):
        self.conn.jconn.mockExceptionOnCommit("java.sql.SQLException", "expected")
        try:
            self.conn.commit()
            self.fail("expected exception")
        except jaydebeapi.DatabaseError as e:
            self.assertEquals(str(e), "java.sql.SQLException: expected")

    def test_runtime_exception_on_commit(self):
        self.conn.jconn.mockExceptionOnCommit("java.lang.RuntimeException", "expected")
        try:
            self.conn.commit()
            self.fail("expected exception")
        except jaydebeapi.InterfaceError as e:
            self.assertEquals(str(e), "java.lang.RuntimeException: expected")

    def test_sql_exception_on_rollback(self):
        self.conn.jconn.mockExceptionOnRollback("java.sql.SQLException", "expected")
        try:
            self.conn.rollback()
            self.fail("expected exception")
        except jaydebeapi.DatabaseError as e:
            self.assertEquals(str(e), "java.sql.SQLException: expected")

    def test_runtime_exception_on_rollback(self):
        self.conn.jconn.mockExceptionOnRollback("java.lang.RuntimeException", "expected")
        try:
            self.conn.rollback()
            self.fail("expected exception")
        except jaydebeapi.InterfaceError as e:
            self.assertEquals(str(e), "java.lang.RuntimeException: expected")

    def test_cursor_with_statement(self):
        self.conn.jconn.mockType("INTEGER")
        with self.conn.cursor() as cursor:
            cursor.execute("dummy stmt")
            self.assertIsNotNone(cursor._connection)
        self.assertIsNone(cursor._connection)

    def test_connection_with_statement(self):
        with jaydebeapi.connect('org.jaydebeapi.mockdriver.MockDriver',
                                       'jdbc:jaydebeapi://dummyurl') as conn:
            self.assertEqual(conn._closed, False)
        self.assertEqual(conn._closed, True)
