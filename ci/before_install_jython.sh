#!/bin/sh
set -e

INST_DIR=$HOME/jython/jython-${JYTHON##*:}
if [ ! -d "$INST_DIR" ]; then
    JYTHON_JAR=$(${TRAVIS_BUILD_DIR}/ci/mvnget.sh "$JYTHON")
    java -jar ${JYTHON_JAR} -s -d "$INST_DIR"
fi
pip install --upgrade virtualenv==15.0.1 tox==3.9.0 coverage==4.5.4
mkdir -p $HOME/bin
ln -s "$INST_DIR"/bin/jython $HOME/bin/
