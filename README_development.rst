================================
 JayDeBeApi - Development notes
================================

Some notes for development.

.. contents::

Setup test requirements
=======================
::
     sudo apt-get install maven
     cd mockdriver
     maven install

     virtualenv ~/.virtualenvs/jaydebeapi-py26 -p /usr/bin/python2.6
     . ~/.virtualenvs/jaydebeapi-py26/bin/activate
     pip install -r dev-requirements.txt -r requirements-python.txt -r test-requirements.txt jip==0.9.3
     envsubst < ci/dot_jip > $VIRTUAL_ENV/.jip
     jip install org.jaydebeapi:mockdriver:1.0-SNAPSHOT
     jip install org.hsqldb:hsqldb:1.8.0.10
     jip install org.xerial:sqlite-jdbc:3.7.2
     export CLASSPATH=$VIRTUAL_ENV/javalib/*
     python setup.py develop
     python test/testsuite.py

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
