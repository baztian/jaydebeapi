#-*- coding: utf-8 -*-

# Copyright 2010-2015 Bastian Bowe
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
# Modified by HenryNebula (2023):
# 1. Remove py2 & Jython support
# 2. Enforce typing for Decimal and temporal types

__version_info__ = (0, 1, 0)
__version__ = ".".join(str(i) for i in __version_info__)

import datetime
import glob
import os
import time
import re
import sys
import warnings

from jaydebeapiarrow.lib.arrow_utils import \
    convert_jdbc_rs_to_arrow_iterator, \
    read_rows_from_arrow_iterator, \
    create_pyarrow_batches_from_list, \
    add_pyarrow_batches_to_statement


def reraise(tp, value, tb=None):
    if value is None:
        value = tp()
    else:
        value = tp(value)
    if tb:
        raise value.with_traceback(tb)
    raise value


# Mapping from java.sql.Types attribute name to attribute value
_jdbc_name_to_const = None

# Mapping from java.sql.Types attribute constant value to it's attribute name
_jdbc_const_to_name = None

_jdbc_connect = None

_java_array_byte = None

_handle_sql_exception = None

old_jpype = False

def _handle_sql_exception_jpype():
    import jpype
    SQLException = jpype.java.sql.SQLException
    exc_info = sys.exc_info()
    if old_jpype:
        clazz = exc_info[1].__javaclass__
        db_err = issubclass(clazz, SQLException)
    else:
        db_err = isinstance(exc_info[1], SQLException)

    if db_err:
        exc_type = DatabaseError
    else:
        exc_type = InterfaceError
        
    reraise(exc_type, exc_info[1], exc_info[2])

def _jdbc_connect_jpype(jclassname, url, driver_args, jars, libs):
    import jpype
    if not jpype.isJVMStarted():
        args = []
        class_path = []
        if jars:
            class_path.extend(jars)
        # print(_get_classpath())
        class_path.extend(_get_classpath())
        class_path.extend(_get_arrow_jar_paths())
        class_path = list(set(class_path))
        # print(class_path)
        if class_path:
            args.append('-Djava.class.path=%s' %
                        os.path.pathsep.join(class_path))
        if libs:
            # path to shared libraries
            libs_path = os.path.pathsep.join(libs)
            args.append('-Djava.library.path=%s' % libs_path)
        # jvm_path = ('/usr/lib/jvm/java-6-openjdk'
        #             '/jre/lib/i386/client/libjvm.so')
        jvm_path = jpype.getDefaultJVMPath()
        global old_jpype
        if hasattr(jpype, '__version__'):
            try:
                ver_match = re.match('\d+\.\d+', jpype.__version__)
                if ver_match:
                    jpype_ver = float(ver_match.group(0))
                    if jpype_ver < 0.7:
                        old_jpype = True
            except ValueError:
                pass
        if old_jpype:
            jpype.startJVM(jvm_path, *args)
        else:
            jpype.startJVM(jvm_path, *args, ignoreUnrecognized=True,
                           convertStrings=True)
    if not jpype.isThreadAttachedToJVM():
        jpype.attachThreadToJVM()
        jpype.java.lang.Thread.currentThread().setContextClassLoader(jpype.java.lang.ClassLoader.getSystemClassLoader())

    # register driver for DriverManager
    jpype.JClass(jclassname)
    if isinstance(driver_args, dict):
        Properties = jpype.java.util.Properties
        info = Properties()
        for k, v in driver_args.items():
            info.setProperty(k, v)
        dargs = [ info ]
    else:
        dargs = driver_args
    return jpype.java.sql.DriverManager.getConnection(url, *dargs)

def _get_classpath():
    """Extract CLASSPATH from system environment as JPype doesn't seem
    to respect that variable.
    """
    try:
        orig_cp = os.environ['CLASSPATH']
    except KeyError:
        return []
    expanded_cp = []
    for i in orig_cp.split(os.path.pathsep):
        expanded_cp.extend(_jar_glob(i))
    return expanded_cp

def _jar_glob(item):
    if item.endswith('*'):
        jars = []
        for p in ['', '/**/']:
            jars.extend(glob.glob('%s' % str(item).rstrip("*") + p + "*.[jJ][aA][rR]", recursive=True))
        return jars
    else:
        return [item]

def _prepare_jpype():
    global _jdbc_connect
    _jdbc_connect = _jdbc_connect_jpype
    global _handle_sql_exception
    _handle_sql_exception = _handle_sql_exception_jpype

_prepare_jpype()


def _get_arrow_jar_paths():
    search_path = os.path.join(os.path.dirname(__file__), "./lib/arrow-jdbc-extension*")
    arrow_jars = list(_jar_glob(search_path))
    assert len(arrow_jars) > 0, f"Can not find arrow-jdbc JAR file at {search_path}"
    return arrow_jars


apilevel = '2.0'
threadsafety = 1
paramstyle = 'qmark'

class DBAPITypeObject(object):
    _mappings = {}
    def __init__(self, group_name, *values):
        """Construct new DB-API 2.0 type object.
        values: Attribute names of java.sql.Types constants"""
        self.values = values
        self.group_name = group_name
        for type_name in values:
            if type_name in DBAPITypeObject._mappings:
                raise ValueError("Non unique mapping for type '%s'" % type_name)
            DBAPITypeObject._mappings[type_name] = self
    def __cmp__(self, other):
        if other in self.values:
            return 0
        if other < self.values:
            return 1
        else:
            return -1
    def __repr__(self):
        return 'DBAPITypeObject(%s)' % ", ".join([repr(i) for i in self.values])
    @classmethod
    def _map_jdbc_type_to_dbapi(cls, jdbc_type_const):
        try:
            type_name = _jdbc_const_to_name[jdbc_type_const]
        except KeyError:
            warnings.warn("Unknown JDBC type with constant value %d. "
                          "Using None as a default type_code." % jdbc_type_const)
            return None
        try:
            return cls._mappings[type_name]
        except KeyError:
            warnings.warn("No type mapping for JDBC type '%s' (constant value %d). "
                          "Using None as a default type_code." % (type_name, jdbc_type_const))
            return None


STRING = DBAPITypeObject('STRING', 'CHAR', 'NCHAR', 'NVARCHAR', 'VARCHAR') # TODO: 'OTHER' not supported

TEXT = DBAPITypeObject('TEXT', 'CLOB', 'LONGVARCHAR', 'LONGNVARCHAR') # TODO: 'NCLOB', 'SQLXML' not supported

BINARY = DBAPITypeObject('BINARY', 'BINARY', 'BLOB', 'LONGVARBINARY', 'VARBINARY')

NUMBER = DBAPITypeObject('NUMBER','BOOLEAN', 'BIGINT', 'BIT', 'INTEGER', 'SMALLINT',
                         'TINYINT')

FLOAT = DBAPITypeObject('FLOAT', 'FLOAT', 'REAL', 'DOUBLE')

DECIMAL = DBAPITypeObject('DECIMAL', 'DECIMAL', 'NUMERIC')

DATE = DBAPITypeObject('DATE', 'DATE')

TIME = DBAPITypeObject('TIME', 'TIME')

DATETIME = DBAPITypeObject('TIMESTAMP', 'TIMESTAMP')

# ROWID = DBAPITypeObject('ROWID', 'ROWID') # TODO: 'ROWID' not supported

# DB-API 2.0 Module Interface Exceptions
class Error(Exception):
    pass

class Warning(Exception):
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
import jpype.dbapi2

def _java_sql_blob(data):
    return _java_array_byte(data)

Binary = _java_sql_blob

def _str_func(func):
    def to_str(*parms):
        return str(func(*parms))
    return to_str

def _ts_converter(*parms):
    if len(parms) >= 7:
        nano = parms[6] * 1000
    else:
        nano = 0
    return jpype.dbapi2.Timestamp(*parms[:6], nano=nano)

TypedDate = lambda *parms: jpype.dbapi2.Date(*parms)
Date = _str_func(datetime.date)

TypedTime = lambda *parms: jpype.dbapi2.Time(*parms)
Time = _str_func(datetime.time)

TypedTimestamp = lambda *parms: _ts_converter(*parms)
Timestamp = _str_func(datetime.datetime)

# DB-API 2.0 Module Interface connect constructor
def connect(jclassname, url, driver_args=None, jars=None, libs=None):
    """Open a connection to a database using a JDBC driver and return
    a Connection instance.

    jclassname: Full qualified Java class name of the JDBC driver.
    url: Database url as required by the JDBC driver.
    driver_args: Dictionary or sequence of arguments to be passed to
           the Java DriverManager.getConnection method. Usually
           sequence of username and password for the db. Alternatively
           a dictionary of connection arguments (where `user` and
           `password` would probably be included). See
           http://docs.oracle.com/javase/7/docs/api/java/sql/DriverManager.html
           for more details
    jars: Jar filename or sequence of filenames for the JDBC driver
    libs: Dll/so filenames or sequence of dlls/sos used as shared
          library by the JDBC driver
    """
    if isinstance(driver_args, str):
        driver_args = [ driver_args ]
    if not driver_args:
       driver_args = []
    if jars:
        if isinstance(jars, str):
            jars = [ jars ]
    else:
        jars = []
    if libs:
        if isinstance(libs, str):
            libs = [ libs ]
    else:
        libs = []
    jconn = _jdbc_connect(jclassname, url, driver_args, jars, libs)
    return Connection(jconn)

# DB-API 2.0 Connection Object
class Connection(object):

    Error = Error
    Warning = Warning
    InterfaceError = InterfaceError
    DatabaseError = DatabaseError
    InternalError = InternalError
    OperationalError = OperationalError
    ProgrammingError = ProgrammingError
    IntegrityError = IntegrityError
    DataError = DataError
    NotSupportedError = NotSupportedError

    def __init__(self, jconn):
        self.jconn = jconn
        self._closed = False

    def close(self):
        if self._closed:
            raise Error()
        self.jconn.close()
        self._closed = True

    def commit(self):
        try:
            self.jconn.commit()
        except:
            _handle_sql_exception()

    def rollback(self):
        try:
            self.jconn.rollback()
        except:
            _handle_sql_exception()

    def cursor(self):
        return Cursor(self)

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.close()

# DB-API 2.0 Cursor Object
class Cursor(object):

    rowcount = -1
    _meta = None
    _prep = None
    _rs = None
    _rs_initial_fetch = True
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
                jdbc_type = m.getColumnType(col)
                if jdbc_type == 0:
                    # PEP-0249: SQL NULL values are represented by the
                    # Python None singleton
                    dbapi_type = None
                else:
                    dbapi_type = DBAPITypeObject._map_jdbc_type_to_dbapi(jdbc_type)
                col_desc = ( m.getColumnName(col),
                             dbapi_type,
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
        self._connection = None

    def _close_last(self):
        """Close the resultset and reset collected meta data.
        """
        if self._rs:
            self._rs.close()
            self._rs_initial_fetch = True
        self._rs = None
        if self._prep:
            self._prep.close()
        self._prep = None
        self._meta = None
        self._description = None

    # def _set_stmt_parms(self, prep_stmt, parameters):
    #     for i in range(len(parameters)):
    #         # print (i, parameters[i], type(parameters[i]))
    #         prep_stmt.setObject(i + 1, parameters[i])

    def _set_stmt_parms(self, statement, parameters):
        batches = create_pyarrow_batches_from_list(parameters)
        add_pyarrow_batches_to_statement(batches, statement)

    def execute(self, operation, parameters=None):
        if self._connection._closed:
            raise Error()
        if not parameters:
            parameters = ()
        self._close_last()
        self._prep = self._connection.jconn.prepareStatement(operation)
        self._set_stmt_parms(self._prep, parameters)
        try:
            is_rs = self._prep.execute()
        except:
            _handle_sql_exception()
        if is_rs:
            self._rs = self._prep.getResultSet()
            self._rs_initial_fetch = True
            self._meta = self._rs.getMetaData()
            self.rowcount = -1
        else:
            self.rowcount = self._prep.getUpdateCount()
        # self._prep.getWarnings() ???

    def executemany(self, operation, seq_of_parameters):
        self._close_last()
        self._prep = self._connection.jconn.prepareStatement(operation)
        self._set_stmt_parms(self._prep, seq_of_parameters)
        update_counts = self._prep.executeBatch()
        # self._prep.getWarnings() ???
        self.rowcount = sum(update_counts)
        self._close_last()

    def fetchone(self):
        if not self._rs:
            raise Error()
        # if not self._rs.isBeforeFirst():
        #     return None

        if self._rs_initial_fetch:
            self._rs_initial_fetch = False
        else:
            return None

        it = convert_jdbc_rs_to_arrow_iterator(self._rs, batch_size=1)
        row = read_rows_from_arrow_iterator(it, nrows=1)
        return tuple(*row) if len(row) == 1 else None

    def fetchmany(self, size=None):
        if not self._rs:
            raise Error()
        # if not self._rs.isBeforeFirst():
        #     return []

        if self._rs_initial_fetch:
            self._rs_initial_fetch = False
        else:
            return []

        if size is None:
            size = self.arraysize

        assert size > 0, f"Fetchmany expects positive size other than size={size}."

        it = convert_jdbc_rs_to_arrow_iterator(self._rs, size)
        rows = read_rows_from_arrow_iterator(it, size)

        return rows

    def fetchall(self):
        if not self._rs:
            raise Error()
        # if not self._rs.isBeforeFirst():
        #     return []

        if self._rs_initial_fetch:
            self._rs_initial_fetch = False
        else:
            return []
        
        it = convert_jdbc_rs_to_arrow_iterator(self._rs)
        rows = read_rows_from_arrow_iterator(it)

        return rows

    # optional nextset() unsupported

    arraysize = 1

    def setinputsizes(self, sizes):
        pass

    def setoutputsize(self, size, column=None):
        pass

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.close()

