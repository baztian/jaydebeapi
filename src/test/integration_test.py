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

from os import path
from unittest import TestCase
import jaydebeapi
import sys

this_dir = path.dirname(path.abspath(__file__))
jar_dir = path.abspath(path.join(this_dir, '..', '..',
                                       'build', 'lib'))
create_sql = path.join(this_dir, 'data', 'create.sql')
insert_sql = path.join(this_dir, 'data', 'insert.sql')

def is_jython():
    return sys.platform.lower().startswith('java')

class IntegrationTest(TestCase):

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

    def setup_jpype(self, jars, libs=None):
        import jpype
        if not jpype.isJVMStarted():
            jvm_path = jpype.getDefaultJVMPath()
            #jvm_path = ('/usr/lib/jvm/java-6-openjdk'
            #            '/jre/lib/i386/client/libjvm.so')
            # path to shared libraries
            args = []
            if libs:
                libs_path = path.pathsep.join(libs)
                args.append('-Djava.library.path=%s' % libs_path)
            class_path = path.pathsep.join(jars)
            args.append('-Djava.class.path=%s' % class_path)
            jpype.startJVM(jvm_path, *args)
        if not jpype.isThreadAttachedToJVM():
            jpype.attachThreadToJVM()

    def connect(self):
        import sqlite3
        return sqlite3.connect(':memory:')

    def connect_(self):
        jar_names = [ 'hsqldb.jar', 'sqlitejdbc-v056.jar', 'sqlite.jar' ]
        jars = [ path.join(jar_dir, i) for i in jar_names ]
        if is_jython():
            sys.path.extend(jars)
        else:
            self.setup_jpype(jars, [jar_dir])
        # http://www.zentus.com/sqlitejdbc/
        conn = jaydebeapi.connect('org.sqlite.JDBC',
                                  'jdbc:sqlite::memory:')
        # http://hsqldb.org/
        # conn = jaydebeapi.connect('org.hsqldb.jdbcDriver',
        #                           'jdbc:hsqldb:mem', 'SA', '')
        # conn = jaydebeapi.connect('com.ibm.db2.jcc.DB2Driver',
        #                           'jdbc:db2://4.100.73.81:50000/db2t',
        #                           getpass.getuser(),
        #                           getpass.getpass())
        # driver from http://www.ch-werner.de/javasqlite/ seems to be
        # crap as it returns decimal values as VARCHAR type
        # conn = jaydebeapi.connect('SQLite.JDBCDriver',
        #                           'jdbc:sqlite:/:memory:')
        return conn
    
    def setUp(self):
        self.conn = self.connect() 
        self.sql_file(create_sql)
        self.sql_file(insert_sql)

    def tearDown(self):
        cursor = self.conn.cursor()
        cursor.execute("drop table konto");
        self.conn.close()

    def test_execute_and_fetch_no_data(self):
        cursor = self.conn.cursor()
        stmt = "select * from konto where konto_id is null"
        cursor.execute(stmt)
        assert [] == cursor.fetchall()

    def test_execute_and_fetch(self):
        cursor = self.conn.cursor()
        cursor.execute("select * from konto")
        result = cursor.fetchall()
        assert [(u'2009-09-10 14:15:22.123456', 18, 12.4, None),
         (u'2009-09-11 14:15:22.123456', 19, 12.9, 1)] == result

    def test_execute_and_fetch_parameter(self):
        cursor = self.conn.cursor()
        cursor.execute("select * from konto where konto_nr = ?", (18,))
        result = cursor.fetchall()
        assert [(u'2009-09-10 14:15:22.123456', 18, 12.4, None)] == result

    def test_execute_and_fetchone(self):
        cursor = self.conn.cursor()
        cursor.execute("select * from konto order by konto_nr")
        result = cursor.fetchone()
        assert (u'2009-09-10 14:15:22.123456', 18, 12.4, None) == result
        cursor.close()

    def test_execute_reset_description_without_execute_result(self):
        """Excpect the descriptions property being reset when no query
        has been made via execute method.
        """
        cursor = self.conn.cursor()
        cursor.execute("select * from konto")
        assert None != cursor.description
        cursor.fetchone()
        cursor.execute("delete from konto")
        assert None == cursor.description

    def test_execute_and_fetchone_after_end(self):
        cursor = self.conn.cursor()
        cursor.execute("select * from konto where konto_nr = ?", (18,))
        cursor.fetchone()
        result = cursor.fetchone()
        assert None is result

    def test_execute_and_fetchmany(self):
        cursor = self.conn.cursor()
        cursor.execute("select * from konto order by konto_nr")
        result = cursor.fetchmany()
        assert [(u'2009-09-10 14:15:22.123456', 18, 12.4, None)] == result
        # TODO: find out why this cursor has to be closed in order to
        # let this test work with sqlite
#        cursor.close()

    def test_executemany(self):
        cursor = self.conn.cursor()
        stmt = "insert into Konto (KONTO_ID, KONTO_NR, SALDO) values (?, ?, ?)"
        parms = (
            ( '2009-09-11 14:15:22.123450', 20, 13.1 ),
            ( '2009-09-11 14:15:22.123451', 21, 13.2 ),
            ( '2009-09-11 14:15:22.123452', 22, 13.3 ),
            )
        cursor.executemany(stmt, parms)
        assert cursor.rowcount == 3
