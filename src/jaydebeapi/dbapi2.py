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

import datetime
import exceptions
import time
import re
import sys

_jdbc_connect = None

def _jdbc_connect_jython(jclassname, *args):
    if _converters is None:
        from java.sql import Types
        types = Types
        types_map = {}
        const_re = re.compile('[A-Z][A-Z_]*$')
        for i in dir(types):
            if const_re.match(i):
                types_map[i] = getattr(types, i)
        _init_converters(types_map)
    # register driver for DriverManager
    __import__(jclassname)
    from java.sql import DriverManager
    return DriverManager.getConnection(*args)

def _prepare_jython():
    global _jdbc_connect
    _jdbc_connect = _jdbc_connect_jython
    # TODO: find solution for jython
    # Binary = buffer

def _jdbc_connect_jpype(jclassname, *args):
    import jpype
    if not jpype.isJVMStarted():
        jpype.startJVM(jpype.getDefaultJVMPath())
    if not jpype.isThreadAttachedToJVM():
        jpype.attachThreadToJVM()
    if _converters is None:
        types = jpype.java.sql.Types
        types_map = {}
        for i in types.__javaclass__.getClassFields():
            types_map[i.getName()] = i.getStaticAttribute()
        _init_converters(types_map)
    # register driver for DriverManager
    jpype.JClass(jclassname)
    return jpype.java.sql.DriverManager.getConnection(*args)

def _prepare_jpype():
    global _jdbc_connect
    _jdbc_connect = _jdbc_connect_jpype
    # TODO: doesn't work for Jython
#    global Binary
#    Binary = buffer

if sys.platform.lower().startswith('java'):
    _prepare_jython()
else:
    _prepare_jpype()

apilevel = '2.0'
threadsafety = 1
paramstyle = 'qmark'

class DBAPITypeObject(object):
    def __init__(self,*values):
        self.values = values
    def __cmp__(self,other):
        if other in self.values:
            return 0
        if other < self.values:
            return 1
        else:
            return -1

STRING = DBAPITypeObject("CHARACTER", "CHAR", "VARCHAR",
                          "CHARACTER VARYING", "CHAR VARYING", "STRING",)

TEXT = DBAPITypeObject("CLOB", "CHARACTER LARGE OBJECT",
                       "CHAR LARGE OBJECT",  "XML",)

BINARY = DBAPITypeObject("BLOB", "BINARY LARGE OBJECT",)

NUMBER = DBAPITypeObject("INTEGER", "INT", "SMALLINT", "BIGINT",)

FLOAT = DBAPITypeObject("FLOAT", "REAL", "DOUBLE", "DECFLOAT")

DECIMAL = DBAPITypeObject("DECIMAL", "DEC", "NUMERIC", "NUM",)

DATE = DBAPITypeObject("DATE",)

TIME = DBAPITypeObject("TIME",)

DATETIME = DBAPITypeObject("TIMESTAMP",)

ROWID = DBAPITypeObject(())

# DB-API 2.0 Module Interface Exceptions
class Error(exceptions.StandardError):
    pass

class Warning(exceptions.StandardError):
    pass

class InterfaceError(Error):
    pass

class DatabaseError(Error):
    pass

class InternalError(DatabaseError):
    pass

class OperationalError(DatabaseError):
    pass

class ProgrammingError(DatabaseError):
    pass

class IntegrityError(DatabaseError):
    pass

class DataError(DatabaseError):
    pass

class NotSupportedError(DatabaseError):
    pass

# DB-API 2.0 Type Objects and Constructors
Date = datetime.date

Time = datetime.time

Timestamp = datetime.datetime

def DateFromTicks(ticks):
    return apply(Date, time.localtime(ticks)[:3])

def TimeFromTicks(ticks):
    return apply(Time, time.localtime(ticks)[3:6])

def TimestampFromTicks(ticks):
    return apply(Timestamp, time.localtime(ticks)[:6])

# DB-API 2.0 Module Interface connect constructor
def connect(jclassname, *args):
    jconn = _jdbc_connect(jclassname, *args)
    return Connection(jconn)

# DB-API 2.0 Connection Object
class Connection(object):

    jconn = None

    def __init__(self, jconn):
        self.jconn = jconn

    def close(self):
        self.jconn.close()

    def commit(self):
        return self.jconn.commit()

    def rollback(self):
        return self.jconn.rollback()

    def cursor(self):
        return Cursor(self)

# DB-API 2.0 Cursor Object
class Cursor(object):

    rowcount = -1
    _meta = None
    _prep = None
    _rs = None
    _description = None

    def __init__(self, connection):
        self._connection = connection

    @property
    def description(self):
        if self._description:
            return self._description
        m = self._meta
        if m:
            count = m.getColumnCount()
            self._description = []
            for col in range(1, count + 1):
                size = m.getColumnDisplaySize(col)
                col_desc = ( m.getColumnName(col),
                             m.getColumnTypeName(col),
                             size,
                             size,
                             m.getPrecision(col),
                             m.getScale(col),
                             m.isNullable(col),
                             )
                self._description.append(col_desc)
            return self._description

#   optional callproc(self, procname, *parameters) unsupported

    def close(self):
        self._close_last()
        self.connection = None

    def _close_last(self):
        """Close the resultset and reset collected meta data.
        """
        if self._rs:
            self._rs.close()
        if self._prep:
            self._prep.close()
        self._rs = None
        self._meta = None
        self._description = None

    def _set_stmt_parms(self, prep_stmt, *parameters):
        for i in range(len(parameters)):
            prep_stmt.setObject(i + 1, parameters[i])

    def execute(self, operation, *parameters):
        self._close_last()
        self._prep = self._connection.jconn.prepareStatement(operation)
        self._set_stmt_parms(self._prep, *parameters)
        is_rs = self._prep.execute()
        self.update_count = self._prep.getUpdateCount()
        if is_rs:
            self._rs = self._prep.getResultSet()
            self._meta = self._rs.getMetaData()
        # self._prep.getWarnings() ???

    def executemany(self, operation, seq_of_parameters):
        self._close_last()
        self._prep = self._connection.jconn.prepareStatement(operation)
        for parameters in seq_of_parameters:
            self._set_stmt_parms(self._prep, *parameters)
            self._prep.addBatch()
        update_counts = self._prep.executeBatch()
        # self._prep.getWarnings() ???
        self.rowcount = sum(update_counts)

    def fetchone(self):
        #raise if not rs
        if not self._rs.next():
            return None
        row = []
        for col in range(1, self._meta.getColumnCount() + 1):
            sqltype = self._meta.getColumnType(col)
            v = self._rs.getObject(col)
            if v:
                converter = _converters.get(sqltype)
                if converter:
                    v = converter(v)
            row.append(v)
        return tuple(row)

    def fetchmany(self, size=None):
        if size is None:
            size = self.arraysize
        self._rs.setFetchSize(size)
        rows = []
        row = None
        for i in xrange(size):
            row = self.fetchone()
            if row is None:
                break
            else:
                rows.append(row)
        # reset fetch size
        if row:
            self._rs.setFetchSize(0)
        return rows

    def fetchall(self):
        rows = []
        while True:
            row = self.fetchone()
            if row is None:
                break
            else:
                rows.append(row)
        return rows

    # optional nextset() unsupported

    arraysize = 1

    def setinputsizes(self, sizes):
        pass

    def setoutputsize(self, size, column):
        pass

def to_datetime(java_val):
#    d=datetime.datetime.strptime(timestmp.toString()[:-7], "%Y-%m-%d %H:%M:%S")
#    return d.replace(microsecond=int(str(timestmp.getNanos())[:6]))
    return java_val.toString()

def to_date(java_val):
#    d=datetime.datetime.strptime(timestmp.toString()[:-7], "%Y-%m-%d %H:%M:%S")
#    return d.replace(microsecond=int(str(timestmp.getNanos())[:6]))
    return java_val.toString()

def to_float(java_val):
    return java_val.doubleValue()

def _init_converters(types_map):
    """Prepares the converters for conversion of java types to python
    objects.
    types_map: Mapping of java.sql.Types field name to java.sql.Types
    field constant value"""
    global _converters
    _converters = {}
    for i in _DEFAULT_CONVERTERS:
        const_val = types_map[i]
        _converters[const_val] = _DEFAULT_CONVERTERS[i]

# Mapping from java.sql.Types field to converter method
_converters = None

_DEFAULT_CONVERTERS = {
    # see
    # http://download.oracle.com/javase/1.4.2/docs/api/java/sql/Types.html
    # for possible keys
    'TIMESTAMP': to_datetime,
    'DATE': to_date,
    'DECIMAL': to_float,
    'NUMERIC': to_float,
}
