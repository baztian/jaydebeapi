=================================================================
 JayDeBeApi - bridge from JDBC database drivers to Python DB-API
=================================================================

.. image:: https://img.shields.io/travis/baztian/jaydebeapi/master.svg
   :target: https://travis-ci.org/baztian/jaydebeapi

.. image:: https://img.shields.io/coveralls/baztian/jaydebeapi/master.svg
    :target: https://coveralls.io/r/baztian/jaydebeapi

.. image:: https://img.shields.io/badge/python-2.6,_2.7,_3.4-blue.svg
    :target: https://pypi.python.org/pypi/JayDeBeApi

.. image:: https://img.shields.io/badge/jython-2.7--rc1-blue.svg
    :target: https://pypi.python.org/pypi/JayDeBeApi

.. image:: https://pypip.in/version/JayDeBeApi/badge.svg
    :target: https://pypi.python.org/pypi/JayDeBeApi

.. image:: https://pypip.in/download/JayDeBeApi/badge.svg
    :target: https://pypi.python.org/pypi/JayDeBeApi/

The JayDeBeApi module allows you to connect from Python code to
databases using Java `JDBC
<http://java.sun.com/products/jdbc/overview.html>`_. It provides a
Python DB-API_ v2.0 to that database.

It works on ordinary Python (cPython) using the JPype_ Java
integration or on `Jython <http://www.jython.org/>`_ to make use of
the Java JDBC driver.

In contrast to zxJDBC from the Jython project JayDeBeApi let's you
access a database with Jython AND Python with only minor code
modifications. JayDeBeApi's future goal is to provide a unique and
fast interface to different types of JDBC-Drivers through a flexible
plug-in mechanism.

.. contents::

Install
=======

You can get and install JayDeBeApi with `pip <http://pip.pypa.io/>`_
::

    $ pip install JayDeBeApi

If you want to install JayDeBeApi in Jython make sure to have pip or
EasyInstall available for it.

Or you can get a copy of the source by cloning from the `JayDeBeApi
github project <https://github.com/baztian/jaydebeapi>`_ and install
with ::

    $ python setup.py install

or if you are using Jython use ::

    $ jython setup.py install

It has been tested with Jython 2.7-rc1.

If you are using cPython ensure that you have installed JPype_
properly. It has been tested with JPype1 0.5.7. Older JPype
installations may cause problems.

Usage
=====

Basically you just import the ``jaydebeapi`` Python module and execute
the ``connect`` method. This gives you a DB-API_ conform connection to
the database.

The first argument to ``connect`` is the name of the Java driver
class. Then you can supply a single argument or a sequence of
arguments that are internally passed to the Java
``DriverManager.getConnection`` method. Usually this is the JDBC
connection URL. See the Javadoc of ``DriverManager`` class for
details.

The next parameter to ``connect`` is optional and specifies the
jar-Files of the driver if your classpath isn't set up sufficiently
yet. The classpath set in ``CLASSPATH`` environment variable will be
honored. See the documentation of your Java runtime environment.

Here is an example:

>>> import jaydebeapi
>>> conn = jaydebeapi.connect('org.hsqldb.jdbcDriver',
...                           ['jdbc:hsqldb:mem:.', 'SA', ''],
...                           '/path/to/hsqldb.jar',)
>>> curs = conn.cursor()
>>> curs.execute('create table CUSTOMER'
...                '("CUST_ID" INTEGER not null,'
...                ' "NAME" VARCHAR not null,'
...                ' primary key ("CUST_ID"))'
...             )
>>> curs.execute("insert into CUSTOMER values (1, 'John')")
>>> curs.execute("select * from CUSTOMER")
>>> curs.fetchall()
[(1, u'John')]

If you're having trouble getting this work check if your ``JAVA_HOME``
environmentvariable is set correctly. For example I have to set it on
my Ubuntu machine like this ::

    $ JAVA_HOME=/usr/lib/jvm/java-6-openjdk python

Supported databases
===================

In theory *every database with a suitable JDBC driver should work*. It
is known to work with the following databases:

+-----------------------------------------+------------------------------------------------+---------------+----------------------+
|Database                                 |JDBC driver                                     |Supported      |Remarks               |
+=========================================+================================================+===============+======================+
|`SQLite                                  |`SqliteJDBC                                     |Good           |Can't interpret       |
|<http://www.sqlite.org/>`_               |<http://www.zentus.com/sqlitejdbc/>`_ v056      |               |selected BLOBs        |
|3                                        |                                                |               |correctly.            |
+-----------------------------------------+------------------------------------------------+---------------+----------------------+
|                                         |`Sqlite Java Wrapper                            |Medium         |Weird type handling.  |
|                                         |<http://www.ch-werner.de/javasqlite/>`_         |               |                      |
|                                         |javasqlite-20110106-win32                       |               |                      |
+-----------------------------------------+------------------------------------------------+---------------+----------------------+
|`Hypersonic SQL (HSQLDB)                 |Builtin                                         |Very Good      |No BLOB support       |
|<http://hsqldb.org/>`_ 1.8.1.3           |                                                |               |by database.          |
|                                         |                                                |               |                      |
+-----------------------------------------+------------------------------------------------+---------------+----------------------+
|`Hypersonic SQL (HSQLDB)                 |Builtin                                         |Medium         |Weird decimal         |
|<http://hsqldb.org/>`_ 2                 |                                                |               |type                  |
|                                         |                                                |               |conversions. No       |
|                                         |                                                |               |BLOB support.         |
+-----------------------------------------+------------------------------------------------+---------------+----------------------+
|`IBM DB2                                 |JDBC type 4 drivers from IBM (``db2jcc.jar``)   |Medium.        |Not thoroughly tested |
|<http://www.ibm.com/software/data/db2/>`_|                                                |               |but seems to work     |
|for z/OS                                 |                                                |               |without problems.     |
+-----------------------------------------+------------------------------------------------+---------------+----------------------+
|Oracle 11g                               |Oracle Thin Driver                              |Medium         |Not thoroughly        |
|                                         |                                                |               |tests. No support for |
|                                         |                                                |               |rading of timestamps  |
|                                         |                                                |               |yet.                  |
+-----------------------------------------+------------------------------------------------+---------------+----------------------+
|Teradata DB                              |terajdbc4.jar                                   |Medium         |A user reported       |
|                                         |                                                |               |success.              |
+-----------------------------------------+------------------------------------------------+---------------+----------------------+
|Other databases                          |Other JDBC drivers                              |Unkown         |Please test yourself  |
|                                         |                                                |               |and report the        |
|                                         |                                                |               |results.              |
+-----------------------------------------+------------------------------------------------+---------------+----------------------+

Contributing
============

Please submit `bugs and patches
<https://github.com/baztian/jaydebeapi/issues>`_. All contributors
will be acknowledged. Thanks!

License
=======

JayDeBeApi is released under the GNU Lesser General Public license
(LGPL). See the file ``COPYING`` and ``COPYING.LESSER`` in the
distribution for details.


Changelog
=========

- Next version - unreleased
- 0.2.0 - 2015-04-26

  - Python 3 support (requires JPype1 >= 0.6.0).

- 0.1.6 - 2015-04-10

  - Fix Jython handling of Java exceptions that don't subclass python Exception

  - Enrich exceptions with message from java SQLExceptions

  - Be more specific about DB API exceptions: Distinguish DatabaseError and
    InterfaceError.

  - Fix typo LONGNARCHAR vs LONGVARCHAR (thanks @datdo for reporting #4)

- 0.1.5 - 2015-03-02

  - Add version number to module.

  - Improve robustness of java to python type conversion.

  - Support Time type.

  - Add DB-API compliant exception handling.

  - Minor documentation improvements.

  - Some development related changes (Host project at github, use
    Travis CI, use JPype1 for tests).

- 0.1.4 - 2013-10-29

  - More convenient way to setup Java classpath. *Important note*
    check the changes to the ``connect`` method and adapt your code.

  - Honor ``CLASSPATH`` if used in JPype mode.

  - Set ``.rowcount`` properly.

  - Changed signature of ``.setoutputsize()`` to be DB-API compliant.

- 0.1.3 - 2011-01-27

  - Fixed DB-API_ violation: Use ``curs.execute('foo ?', (bar, baz))``
    instead of ``curs.execute('foo ?', bar, baz)``.

  - Free resources after ``executemany`` call.

  - Improved type handling. Initial support for BLOB columns.

- 0.1.2 - 2011-01-25

  - ``easy_install JayDeBeApi`` should really work.

- 0.1.1 - 2010-12-12

  - Fixed bug #688290 "NULL values with converters error on fetch".
  - Fixed bug #684909 "Selecting ROWIDs errors out on fetch".

- 0.1 - 2010-08-10

  - Initial release.

To do
=====

- Extract Java calls to separate Java methods to increase performance.
- Check if https://code.launchpad.net/dbapi-compliance can help making
  JayDeBeApi more DB-API compliant.
- Test it on different databases and provide a flexible db specific
  pluign mechanism.
- SQLAlchemy modules (separate project)

.. _DB-API: http://www.python.org/dev/peps/pep-0249/
.. _JPype: https://pypi.python.org/pypi/JPype1/
