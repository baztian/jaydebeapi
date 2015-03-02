================================
 JayDeBeApi - Development notes
================================

Some notes for development.

.. contents::

Build a new release
===================

1. Sync the branch. ::

     $ git checkout master
     $ git pull

2. Do your changes.

3. Add a changelog entry to ``README.rst`` below ``Next version``.

4. Commit and push your changes. ::

     $ git commit -m "my comment"
     $ git push

5. Wait for travis CI build to finish successfully.

6. Bump version ::

     $ bumpversion [major|minor|patch]

7. Run setuptools to ensure everything is working as expected. ::

     $ python setup.py sdist bdist_wheel upload

8. Check the files in ``dist/`` for unwanted or missing files.

9. Send new version and tags to github origin. ::

     $ git push origin master --tags
