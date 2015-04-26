#!/bin/bash
set -e

JYTHON_JAR=$(${TRAVIS_BUILD_DIR}/ci/mvnget.sh $JYTHON)
java -jar ${JYTHON_JAR} -s -d $HOME/jython

$HOME/jython/bin/jython -m ensurepip

# Install the latest virtualenv compatible with Jython
$HOME/jython/bin/pip install virtualenv==1.9.1
$HOME/jython/bin/virtualenv $HOME/myvirtualenv
