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

__version_info__ = (1, 2, 3)
__version__ = ".".join(str(i) for i in __version_info__)

import datetime
import glob
import os
import time
import re
import sys
import warnings

PY2 = sys.version_info[0] == 2

if PY2:
    # Ideas stolen from the six python 2 and 3 compatibility layer
    def exec_(_code_, _globs_=None, _locs_=None):
        """Execute code in a namespace."""
        if _globs_ is None:
            frame = sys._getframe(1)
            _globs_ = frame.f_globals
            if _locs_ is None:
                _locs_ = frame.f_locals
            del frame
        elif _locs_ is None:
            _locs_ = _globs_
        exec("""exec _code_ in _globs_, _locs_""")

    exec_("""def reraise(tp, value, tb=None):
    raise tp, value, tb
""")
else:
    def reraise(tp, value, tb=None):
        if value is None:
            value = tp()
        else:
            value = tp(value)
        if tb:
            raise value.with_traceback(tb)
        raise value

if PY2:
    string_type = basestring
else:
    string_type = str

# Mapping from java.sql.Types attribute name to attribute value
_jdbc_name_to_const = None

# Mapping from java.sql.Types attribute constant value to it's attribute name
_jdbc_const_to_name = None

_jdbc_connect = None

_java_array_byte = None

_handle_sql_exception = None

old_jpype = False

def _handle_sql_exception_jython():
    from java.sql import SQLException
    exc_info = sys.exc_info()
    if isinstance(exc_info[1], SQLException):
        exc_type = DatabaseError
    else:
        exc_type = InterfaceError
    reraise(exc_type, exc_info[1], exc_info[2])

def _jdbc_connect_jython(jclassname, url, driver_args, jars, libs):
    if _jdbc_name_to_const is None:
        from java.sql import Types
        types = Types
        types_map = {}
        const_re = re.compile('[A-Z][A-Z_]*$')
        for i in dir(types):
            if const_re.match(i):
                types_map[i] = getattr(types, i)
        _init_types(types_map)
    global _java_array_byte
    if _java_array_byte is None:
        import jarray
        def _java_array_byte(data):
            return jarray.array(data, 'b')
    # register driver for DriverManager
    jpackage = jclassname[:jclassname.rfind('.')]
    dclassname = jclassname[jclassname.rfind('.') + 1:]
    # print jpackage
    # print dclassname
    # print jpackage
    from java.lang import Class
    from java.lang import ClassNotFoundException
    try:
        Class.forName(jclassname).newInstance()
    except ClassNotFoundException:
        if not jars:
            raise
        _jython_set_classpath(jars)
        Class.forName(jclassname).newInstance()
    from java.sql import DriverManager
    if isinstance(driver_args, dict):
        from java.util import Properties
        info = Properties()
        for k, v in driver_args.items():
            info.setProperty(k, v)
        dargs = [ info ]
    else:
        dargs = driver_args
    return DriverManager.getConnection(url, *dargs)

def _jython_set_classpath(jars):
    '''
    import a jar at runtime (needed for JDBC [Class.forName])

    adapted by Bastian Bowe from
    http://stackoverflow.com/questions/3015059/jython-classpath-sys-path-and-jdbc-drivers
    '''
    from java.net import URL, URLClassLoader
    from java.lang import ClassLoader
    from java.io import File
    m = URLClassLoader.getDeclaredMethod("addURL", [URL])
    m.accessible = 1
    urls = [File(i).toURL() for i in jars]
    m.invoke(ClassLoader.getSystemClassLoader(), urls)

def _prepare_jython():
    global _jdbc_connect
    _jdbc_connect = _jdbc_connect_jython
    global _handle_sql_exception
    _handle_sql_exception = _handle_sql_exception_jython

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
        class_path.extend(_get_classpath())
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
    if _jdbc_name_to_const is None:
        types = jpype.java.sql.Types
        types_map = {}
        if old_jpype:
          for i in types.__javaclass__.getClassFields():
            const = i.getStaticAttribute()
            types_map[i.getName()] = const
        else:
          for i in types.class_.getFields():
            if jpype.java.lang.reflect.Modifier.isStatic(i.getModifiers()):
              const = i.get(None)
              types_map[i.getName()] = const 
        _init_types(types_map)
    global _java_array_byte
    if _java_array_byte is None:
        def _java_array_byte(data):
            return jpype.JArray(jpype.JByte, 1)(data)
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
        return glob.glob('%s.[jJ][aA][rR]' % item)
    else:
        return [item]

def _prepare_jpype():
    global _jdbc_connect
    _jdbc_connect = _jdbc_connect_jpype
    global _handle_sql_exception
    _handle_sql_exception = _handle_sql_exception_jpype

if sys.platform.lower().startswith('java'):
    _prepare_jython()
else:
    _prepare_jpype()

apilevel = '2.0'
threadsafety = 1
paramstyle = 'qmark'

class DBAPITypeObject(object):
    _mappings = {}
    def __init__(self, *values):
        """Construct new DB-API 2.0 type object.
        values: Attribute names of java.sql.Types constants"""
        self.values = values
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


STRING = DBAPITypeObject('CHAR', 'NCHAR', 'NVARCHAR', 'VARCHAR', 'OTHER')

TEXT = DBAPITypeObject('CLOB', 'LONGVARCHAR', 'LONGNVARCHAR', 'NCLOB', 'SQLXML')

BINARY = DBAPITypeObject('BINARY', 'BLOB', 'LONGVARBINARY', 'VARBINARY')

NUMBER = DBAPITypeObject('BOOLEAN', 'BIGINT', 'BIT', 'INTEGER', 'SMALLINT',
                         'TINYINT')

FLOAT = DBAPITypeObject('FLOAT', 'REAL', 'DOUBLE')

DECIMAL = DBAPITypeObject('DECIMAL', 'NUMERIC')

DATE = DBAPITypeObject('DATE')

TIME = DBAPITypeObject('TIME')

DATETIME = DBAPITypeObject('TIMESTAMP')

ROWID = DBAPITypeObject('ROWID')

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

def _java_sql_blob(data):
    return _java_array_byte(data)

Binary = _java_sql_blob

def _str_func(func):
    def to_str(*parms):
        return str(func(*parms))
    return to_str

Date = _str_func(datetime.date)

Time = _str_func(datetime.time)

Timestamp = _str_func(datetime.datetime)

def DateFromTicks(ticks):
    return apply(Date, time.localtime(ticks)[:3])

def TimeFromTicks(ticks):
    return apply(Time, time.localtime(ticks)[3:6])

def TimestampFromTicks(ticks):
    return apply(Timestamp, time.localtime(ticks)[:6])

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
    if isinstance(driver_args, string_type):
        driver_args = [ driver_args ]
    if not driver_args:
       driver_args = []
    if jars:
        if isinstance(jars, string_type):
            jars = [ jars ]
    else:
        jars = []
    if libs:
        if isinstance(libs, string_type):
            libs = [ libs ]
    else:
        libs = []
    jconn = _jdbc_connect(jclassname, url, driver_args, jars, libs)
    return Connection(jconn, _converters)

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

    def __init__(self, jconn, converters):
        self.jconn = jconn
        self._closed = False
        self._converters = converters

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
        return Cursor(self, self._converters)

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
    _description = None

    def __init__(self, connection, converters):
        self._connection = connection
        self._converters = converters

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
        self._rs = None
        if self._prep:
            self._prep.close()
        self._prep = None
        self._meta = None
        self._description = None

    def _set_stmt_parms(self, prep_stmt, parameters):
        for i in range(len(parameters)):
            # print (i, parameters[i], type(parameters[i]))
            prep_stmt.setObject(i + 1, parameters[i])

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
            self._meta = self._rs.getMetaData()
            self.rowcount = -1
        else:
            self.rowcount = self._prep.getUpdateCount()
        # self._prep.getWarnings() ???

    def executemany(self, operation, seq_of_parameters):
        self._close_last()
        self._prep = self._connection.jconn.prepareStatement(operation)
        for parameters in seq_of_parameters:
            self._set_stmt_parms(self._prep, parameters)
            self._prep.addBatch()
        update_counts = self._prep.executeBatch()
        # self._prep.getWarnings() ???
        self.rowcount = sum(update_counts)
        self._close_last()

    def fetchone(self):
        if not self._rs:
            raise Error()
        if not self._rs.next():
            return None
        row = []
        for col in range(1, self._meta.getColumnCount() + 1):
            sqltype = self._meta.getColumnType(col)
            converter = self._converters.get(sqltype, _unknownSqlTypeConverter)
            v = converter(self._rs, col)
            row.append(v)
        return tuple(row)

    def fetchmany(self, size=None):
        if not self._rs:
            raise Error()
        if size is None:
            size = self.arraysize
        # TODO: handle SQLException if not supported by db
        self._rs.setFetchSize(size)
        rows = []
        row = None
        for i in range(size):
            row = self.fetchone()
            if row is None:
                break
            else:
                rows.append(row)
        # reset fetch size
        if row:
            # TODO: handle SQLException if not supported by db
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

    def setoutputsize(self, size, column=None):
        pass

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.close()

def _unknownSqlTypeConverter(rs, col):
    return rs.getObject(col)

def _to_datetime(rs, col):
    java_val = rs.getTimestamp(col)
    if not java_val:
        return
    d = datetime.datetime.strptime(str(java_val)[:19], "%Y-%m-%d %H:%M:%S")
    d = d.replace(microsecond=int(str(java_val.getNanos())[:6]))
    return str(d)

def _to_time(rs, col):
    java_val = rs.getTime(col)
    if not java_val:
        return
    return str(java_val)

def _to_date(rs, col):
    java_val = rs.getDate(col)
    if not java_val:
        return
    # The following code requires Python 3.3+ on dates before year 1900.
    # d = datetime.datetime.strptime(str(java_val)[:10], "%Y-%m-%d")
    # return d.strftime("%Y-%m-%d")
    # Workaround / simpler soltution (see
    # https://github.com/baztian/jaydebeapi/issues/18):
    return str(java_val)[:10]

def _to_binary(rs, col):
    java_val = rs.getObject(col)
    if java_val is None:
        return
    return str(java_val)

def _java_to_py(java_method):
    def to_py(rs, col):
        java_val = rs.getObject(col)
        if java_val is None:
            return
        if PY2 and isinstance(java_val, (string_type, int, long, float, bool)):
            return java_val
        elif isinstance(java_val, (string_type, int, float, bool)):
            return java_val
        return getattr(java_val, java_method)()
    return to_py

def _java_to_py_bigdecimal():
    def to_py(rs, col):
        java_val = rs.getObject(col)
        if java_val is None:
            return
        if hasattr(java_val, 'scale'):
            scale = java_val.scale()
            if scale == 0:
                return java_val.longValue()
            else:
                return java_val.doubleValue()
        else:
            return float(java_val)
    return to_py

_to_double = _java_to_py('doubleValue')

_to_int = _java_to_py('intValue')

_to_boolean = _java_to_py('booleanValue')

_to_decimal = _java_to_py_bigdecimal()

def _init_types(types_map):
    global _jdbc_name_to_const
    _jdbc_name_to_const = types_map
    global _jdbc_const_to_name
    _jdbc_const_to_name = dict((y,x) for x,y in types_map.items())
    _init_converters(types_map)

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
    # http://download.oracle.com/javase/8/docs/api/java/sql/Types.html
    # for possible keys
    'TIMESTAMP': _to_datetime,
    'TIME': _to_time,
    'DATE': _to_date,
    'BINARY': _to_binary,
    'DECIMAL': _to_decimal,
    'NUMERIC': _to_decimal,
    'DOUBLE': _to_double,
    'FLOAT': _to_double,
    'TINYINT': _to_int,
    'INTEGER': _to_int,
    'SMALLINT': _to_int,
    'BOOLEAN': _to_boolean,
    'BIT': _to_boolean
}
