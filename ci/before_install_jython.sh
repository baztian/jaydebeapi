#!/bin/sh
set -e

INST_DIR=$HOME/jython/jython-${JYTHON##*:}
if [ ! -d "$INST_DIR" ]; then
    JYTHON_JAR=$(${PWD}/ci/mvnget.sh "$JYTHON")
    java -jar ${JYTHON_JAR} -s -d "$INST_DIR"
fi
pip install --upgrade virtualenv==15.1.0 tox==3.9.0
sudo ln -s "$INST_DIR"/bin/jython /usr/local/bin/
which jython
jython --version
echo "WHICH"
