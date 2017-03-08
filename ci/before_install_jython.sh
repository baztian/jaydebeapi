#!/bin/sh
set -e

JYTHON_JAR=$(${TRAVIS_BUILD_DIR}/ci/mvnget.sh "$JYTHON")
java -jar ${JYTHON_JAR} -s -d $HOME/jython
mkdir -p $HOME/bin
ln -s $HOME/jython/bin/jython $HOME/bin/
