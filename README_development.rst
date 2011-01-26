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

3. Add a changelog entry to ``README.rst``.

4. Increase version in ``setup.py``.

5. Run setuptools to ensure everything is working as expected. ::

    $ python setup.py sdist

6. Commit your changes. ::

    $ bzr ci -m "my comment"

7. Tag for the new version. ::

    $ bzr tag jaydebeapi-0.1.2

8. Send changes to launchpad. ::

    $ bzr push

9. Publish new release on PyPi. ::

    $ python setup.py sdist --formats=gztar upload
