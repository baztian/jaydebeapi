=================================================================
 JayDeBeApi - bridge from JDBC database drivers to Python DB-API
=================================================================

.. image:: https://img.shields.io/travis/baztian/jaydebeapi/master.svg
   :target: https://travis-ci.org/baztian/jaydebeapi

.. image:: https://img.shields.io/coveralls/baztian/jaydebeapi/master.svg
    :target: https://coveralls.io/r/baztian/jaydebeapi

.. image:: https://img.shields.io/badge/python-2.6,_2.7,_3.4-blue.svg
    :target: https://pypi.python.org/pypi/JayDeBeApi/

.. image:: https://img.shields.io/badge/jython-2.7.0-blue.svg
    :target: https://pypi.python.org/pypi/JayDeBeApi/

.. image:: https://img.shields.io/github/tag/baztian/jaydebeapi.svg
    :target: https://pypi.python.org/pypi/JayDeBeApi/

.. image:: https://img.shields.io/pypi/dm/JayDeBeApi.svg
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

It has been tested with Jython 2.7.0.

If you are using cPython ensure that you have installed JPype_
properly. It has been tested with JPype1 0.5.7. Older JPype
installations may cause problems.

Usage
=====

Basically you just import the ``jaydebeapi`` Python module and execute
the ``connect`` method. This gives you a DB-API_ conform connection to
the database.

The first argument to ``connect`` is the name of the Java driver
class. The second argument is a string with the JDBC connection
URL. Third you can optionally supply a sequence consisting of user and
password or alternatively a dictionary containing arguments that are
internally passed as properties to the Java
``DriverManager.getConnection`` method. See the Javadoc of
``DriverManager`` class for details.

The next parameter to ``connect`` is optional as well and specifies
the jar-Files of the driver if your classpath isn't set up
sufficiently yet. The classpath set in ``CLASSPATH`` environment
variable will be honored. See the documentation of your Java runtime
environment.

Here is an example:

>>> import jaydebeapi
>>> conn = jaydebeapi.connect("org.hsqldb.jdbcDriver",
...                           "jdbc:hsqldb:mem:.",
...                           ["SA", ""],
...                           "/path/to/hsqldb.jar",)
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
>>> curs.close()
>>> conn.close()

An alternative way to establish connection using connection
properties:

>>> conn = jaydebeapi.connect("org.hsqldb.jdbcDriver",
...                           "jdbc:hsqldb:mem:.",
...                           {'user': "SA", 'password': "",
...                            'other_property': "foobar"},
...                           "/path/to/hsqldb.jar",)


If you're having trouble getting this work check if your ``JAVA_HOME``
environmentvariable is set correctly. For example I have to set it on
my Ubuntu machine like this ::

    $ JAVA_HOME=/usr/lib/jvm/java-8-openjdk python

Supported databases
===================

In theory *every database with a suitable JDBC driver should work*. It
is confirmed to work with the following databases:

* SQLite
* Hypersonic SQL (HSQLDB)
* IBM DB2
* IBM DB2 for mainframes
* Oracle
* Teradata DB
* Netezza
* Mimer DB
* Microsoft SQL Server
* MySQL
* PostgreSQL
* many more...

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
- 1.1.1 - 2017-03-21

  - Don't fail on dates before 1900 on Python < 3.

- 1.1.0 - 2017-03-19

  - Support BIT and TINYINT type mappings (thanks @Mokubyow for
    reporting the issue).

- 1.0.0 - 2017-01-10

  - Allow for db properties to be passed to the connect
    method. *Probably incompatible to code based on previous
    versions.* See documentation of the connect method. (Thanks
    @testlnord for you efforts and the patience.)

  - New major version due to possible api incompatibility.

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
