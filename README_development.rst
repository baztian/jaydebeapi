================================
 JayDeBeApi - Development notes
================================

Some notes for development.

.. contents::

Build a new release
===================

1. Sync the branch. ::

    $ bzr pull

2. Do your changes.

3. Assert the right connect method is configured for tests.

4. Run test suite. Once for cPython, once for Jython and ideally
   against all accessible databases. ::

    $ nosetests

4. Add a changelog entry to ``README.rst``.

5. Increase version in ``setup.py``.

6. Run setuptools to ensure everything is working as expected. ::

    $ python setup.py sdist --formats=gztar

7. Check the file createt by sdist for unwanted or missing files.

8. Install the sdist in a fresh virtualenv. ::

    $ virtualenv tmp
    $ . tmp/bin/activate
    $ easy_install path_to_build_folder/jaydebeapi-0.x.tar.gz

6. Commit your changes. ::

    $ bzr ci -m "my comment"

7. Tag for the new version. ::

    $ bzr tag jaydebeapi-PUT-VERSION-HERE

8. Send changes to launchpad. ::

    $ bzr push

9. Publish new release on PyPi. ::

    $ python setup.py sdist --formats=gztar upload
