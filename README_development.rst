================================
 JayDeBeApi - Development notes
================================

Some notes for development.

.. contents::

Setup test requirements
=======================

::
    sudo apt-get install python2.7-dev python3-dev python3-venv g++ maven
    cd <JAYDEBEAPI_WORKDIR>
    python3 -m venv env
    . env/bin/activate
    pip install -rdev-requirements.txt

    # Install Jython 2.7
    ci/mvnget.sh org.python:jython-installer:2.7.0
    java -jar jython-installer-2.7.0.jar && rm jython-installer-2.7.0.jar
    # add jython to your path

    # Install Python 2.6
    sudo add-apt-repository ppa:fkrull/deadsnakes
    sudo apt-get update
    sudo apt-get install python2.6 python2.6-dev

    # run tests for all supported envs
    tox

    # execute stuff on specific env (examples)
    tox -e py3-driver-mock -- python
    tox -e py3-driver-mock -- python test/testsuite.py test_mock.MockTest.test_sql_exception_on_commit

    # activate and work on specific env
    . .tox/py35-driver-mock/bin/activate
    export CLASSPATH=$VIRTUAL_ENV/javalib/*
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

     $ python setup.py sdist bdist_wheel upload -r pypitest

8. Check the files in ``dist/`` for unwanted or missing files.

9. Send new version and tags to github origin. ::

     $ git push origin master --tags
