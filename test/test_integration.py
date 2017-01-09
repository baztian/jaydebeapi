#-*- coding: utf-8 -*-

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

import jaydebeapi

import os
import sys
import threading

try:
    import unittest2 as unittest
except ImportError:
    import unittest

_THIS_DIR = os.path.dirname(os.path.abspath(__file__))

PY26 = not sys.version_info >= (2, 7)

def is_jython():
    return sys.platform.lower().startswith('java')

if PY26 and not is_jython:
    memoryview = buffer

class IntegrationTestBase(object):

    def sql_file(self, filename):
        f = open(filename, 'r')
        try:
            lines = f.readlines()
        finally:
            f.close()
        stmt = []
        stmts = []
        for i in lines:
            stmt.append(i)
            if ";" in i:
                stmts.append(" ".join(stmt))
                stmt = []
        cursor = self.conn.cursor()
        for i in stmts:
            cursor.execute(i)

    def setUp(self):
        (self.dbapi, self.conn) = self.connect()
        self.setUpSql()

    def setUpSql(self):
        raise NotImplementedError

    def connect(self):
        raise NotImplementedError

    def tearDown(self):
        cursor = self.conn.cursor()
        cursor.execute("drop table ACCOUNT");
        self.conn.close()

    def test_execute_and_fetch_no_data(self):
        cursor = self.conn.cursor()
        stmt = "select * from ACCOUNT where ACCOUNT_ID is null"
        cursor.execute(stmt)
        self.assertEqual(cursor.fetchall(), [])

    def test_execute_and_fetch(self):
        cursor = self.conn.cursor()
        cursor.execute("select ACCOUNT_ID, ACCOUNT_NO, BALANCE, BLOCKING " \
                       "from ACCOUNT")
        result = cursor.fetchall()
        self.assertEqual(result, [(u'2009-09-10 14:15:22.123456', 18, 12.4, None),
                                  (u'2009-09-11 14:15:22.123456', 19, 12.9, 1)])

    def test_execute_and_fetch_parameter(self):
        cursor = self.conn.cursor()
        cursor.execute("select ACCOUNT_ID, ACCOUNT_NO, BALANCE, BLOCKING " \
                       "from ACCOUNT where ACCOUNT_NO = ?", (18,))
        result = cursor.fetchall()
        self.assertEqual(result, [(u'2009-09-10 14:15:22.123456', 18, 12.4, None)])

    def test_execute_and_fetchone(self):
        cursor = self.conn.cursor()
        cursor.execute("select ACCOUNT_ID, ACCOUNT_NO, BALANCE, BLOCKING " \
                       "from ACCOUNT order by ACCOUNT_NO")
        result = cursor.fetchone()
        self.assertEqual(result, (u'2009-09-10 14:15:22.123456', 18, 12.4, None))
        cursor.close()

    def test_execute_reset_description_without_execute_result(self):
        """Expect the descriptions property being reset when no query
        has been made via execute method.
        """
        cursor = self.conn.cursor()
        cursor.execute("select * from ACCOUNT")
        self.assertIsNotNone(cursor.description)
        cursor.fetchone()
        cursor.execute("delete from ACCOUNT")
        self.assertIsNone(cursor.description)

    def test_execute_and_fetchone_after_end(self):
        cursor = self.conn.cursor()
        cursor.execute("select * from ACCOUNT where ACCOUNT_NO = ?", (18,))
        cursor.fetchone()
        result = cursor.fetchone()
        self.assertIsNone(result)

    def test_execute_and_fetchmany(self):
        cursor = self.conn.cursor()
        cursor.execute("select ACCOUNT_ID, ACCOUNT_NO, BALANCE, BLOCKING " \
                       "from ACCOUNT order by ACCOUNT_NO")
        result = cursor.fetchmany()
        self.assertEqual(result, [(u'2009-09-10 14:15:22.123456', 18, 12.4, None)])
        # TODO: find out why this cursor has to be closed in order to
        # let this test work with sqlite if __del__ is not overridden
        # in cursor
        # cursor.close()

    def test_executemany(self):
        cursor = self.conn.cursor()
        stmt = "insert into ACCOUNT (ACCOUNT_ID, ACCOUNT_NO, BALANCE) " \
               "values (?, ?, ?)"
        parms = (
            ( '2009-09-11 14:15:22.123450', 20, 13.1 ),
            ( '2009-09-11 14:15:22.123451', 21, 13.2 ),
            ( '2009-09-11 14:15:22.123452', 22, 13.3 ),
            )
        cursor.executemany(stmt, parms)
        self.assertEqual(cursor.rowcount, 3)

    def test_execute_types(self):
        cursor = self.conn.cursor()
        stmt = "insert into ACCOUNT (ACCOUNT_ID, ACCOUNT_NO, BALANCE, " \
               "BLOCKING, DBL_COL, OPENED_AT, VALID, PRODUCT_NAME) " \
               "values (?, ?, ?, ?, ?, ?, ?, ?)"
        d = self.dbapi
        account_id = d.Timestamp(2010, 1, 26, 14, 31, 59)
        account_no = 20
        balance = 1.2
        blocking = 10.0
        dbl_col = 3.5
        opened_at = d.Date(2008, 2, 27)
        valid = 1
        product_name = u'Savings account'
        parms = (account_id, account_no, balance, blocking, dbl_col,
                 opened_at, valid, product_name)
        cursor.execute(stmt, parms)
        stmt = "select ACCOUNT_ID, ACCOUNT_NO, BALANCE, BLOCKING, " \
               "DBL_COL, OPENED_AT, VALID, PRODUCT_NAME " \
               "from ACCOUNT where ACCOUNT_NO = ?"
        parms = (20, )
        cursor.execute(stmt, parms)
        result = cursor.fetchone()
        cursor.close()
        exp = ( '2010-01-26 14:31:59', account_no, balance, blocking,
                 dbl_col, '2008-02-27', valid, product_name )
        self.assertEqual(result, exp)

    def test_execute_type_time(self):
        cursor = self.conn.cursor()
        stmt = "insert into ACCOUNT (ACCOUNT_ID, ACCOUNT_NO, BALANCE, " \
               "OPENED_AT_TIME) " \
               "values (?, ?, ?, ?)"
        d = self.dbapi
        account_id = d.Timestamp(2010, 1, 26, 14, 31, 59)
        account_no = 20
        balance = 1.2
        opened_at_time = d.Time(13, 59, 59)
        parms = (account_id, account_no, balance, opened_at_time)
        cursor.execute(stmt, parms)
        stmt = "select ACCOUNT_ID, ACCOUNT_NO, BALANCE, OPENED_AT_TIME " \
               "from ACCOUNT where ACCOUNT_NO = ?"
        parms = (20, )
        cursor.execute(stmt, parms)
        result = cursor.fetchone()
        cursor.close()
        exp = ( '2010-01-26 14:31:59', account_no, balance, '13:59:59' )
        self.assertEqual(result, exp)

    def test_execute_different_rowcounts(self):
        cursor = self.conn.cursor()
        stmt = "insert into ACCOUNT (ACCOUNT_ID, ACCOUNT_NO, BALANCE) " \
               "values (?, ?, ?)"
        parms = (
            ( '2009-09-11 14:15:22.123450', 20, 13.1 ),
            ( '2009-09-11 14:15:22.123452', 22, 13.3 ),
            )
        cursor.executemany(stmt, parms)
        self.assertEqual(cursor.rowcount, 2)
        parms = ( '2009-09-11 14:15:22.123451', 21, 13.2 )
        cursor.execute(stmt, parms)
        self.assertEqual(cursor.rowcount, 1)
        cursor.execute("select * from ACCOUNT")
        self.assertEqual(cursor.rowcount, -1)

class SqliteTestBase(IntegrationTestBase):

    def setUpSql(self):
        self.sql_file(os.path.join(_THIS_DIR, 'data', 'create.sql'))
        self.sql_file(os.path.join(_THIS_DIR, 'data', 'insert.sql'))

    def test_execute_type_blob(self):
        cursor = self.conn.cursor()
        stmt = "insert into ACCOUNT (ACCOUNT_ID, ACCOUNT_NO, BALANCE, " \
               "STUFF) values (?, ?, ?, ?)"
        binary_stuff = 'abcdef'.encode('UTF-8')
        stuff = self.dbapi.Binary(binary_stuff)
        parms = ('2009-09-11 14:15:22.123450', 20, 13.1, stuff)
        cursor.execute(stmt, parms)
        stmt = "select STUFF from ACCOUNT where ACCOUNT_NO = ?"
        parms = (20, )
        cursor.execute(stmt, parms)
        result = cursor.fetchone()
        cursor.close()
        value = result[0]
        self.assertEqual(value, memoryview(binary_stuff))

@unittest.skipIf(is_jython(), "requires python")
class SqlitePyTest(SqliteTestBase, unittest.TestCase):

    def connect(self):
        import sqlite3
        return sqlite3, sqlite3.connect(':memory:')

    def test_execute_type_time(self):
        """Time type not supported by PySqlite"""

class SqliteXerialTest(SqliteTestBase, unittest.TestCase):

    def connect(self):
        #http://bitbucket.org/xerial/sqlite-jdbc
        # sqlite-jdbc-3.7.2.jar
        driver, url = 'org.sqlite.JDBC', 'jdbc:sqlite::memory:'
        # db2jcc
        # driver, driver_args = 'com.ibm.db2.jcc.DB2Driver', \
        #    ['jdbc:db2://4.100.73.81:50000/db2t', 'user', 'passwd']
        # driver from http://www.ch-werner.de/javasqlite/ seems to be
        # crap as it returns decimal values as VARCHAR type
        # sqlite.jar
        # driver, driver_args = 'SQLite.JDBCDriver', 'jdbc:sqlite:/:memory:'
        # Oracle Thin Driver
        # driver, driver_args = 'oracle.jdbc.OracleDriver', \
        #     ['jdbc:oracle:thin:@//hh-cluster-scan:1521/HH_TPP',
        #      'user', 'passwd']
        return jaydebeapi, jaydebeapi.connect(driver, url)

    @unittest.skipUnless(is_jython(), "don't know how to support blob")
    def test_execute_type_blob(self):
        return super(SqliteXerialTest, self).test_execute_type_blob()

class HsqldbTest(IntegrationTestBase, unittest.TestCase):

    def connect(self):
        # http://hsqldb.org/
        # hsqldb.jar
        driver, url, driver_args = ( 'org.hsqldb.jdbcDriver',
                                     'jdbc:hsqldb:mem:.',
                                     ['SA', ''] )
        return jaydebeapi, jaydebeapi.connect(driver, url, driver_args)

    def setUpSql(self):
        self.sql_file(os.path.join(_THIS_DIR, 'data', 'create_hsqldb.sql'))
        self.sql_file(os.path.join(_THIS_DIR, 'data', 'insert.sql'))

class PropertiesDriverArgsPassingTest(unittest.TestCase):

    def test_connect_with_sequence(self):
        driver, url, driver_args = ( 'org.hsqldb.jdbcDriver',
                                     'jdbc:hsqldb:mem:.',
                                     ['SA', ''] )
        jaydebeapi.connect(driver, url, driver_args)

    def test_connect_with_properties(self):
        driver, url, driver_args = ( 'org.hsqldb.jdbcDriver',
                                     'jdbc:hsqldb:mem:.',
                                     {'user': 'SA', 'password': '' } )
        jaydebeapi.connect(driver, url, driver_args)
