#!/bin/sh
set -e

INST_DIR=$HOME/jython/jython-${JYTHON##*:}
if [ ! -d "$INST_DIR" ]; then
    JYTHON_JAR=$(${TRAVIS_BUILD_DIR}/ci/mvnget.sh "$JYTHON")
    java -jar ${JYTHON_JAR} -s -d "$INST_DIR"
fi
mkdir -p $HOME/bin
ln -s "$INST_DIR"/bin/jython $HOME/bin/
