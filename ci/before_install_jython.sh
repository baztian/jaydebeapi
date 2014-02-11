#!/bin/bash
set -e

pip install jip==0.7
jip install org.python:$JYTHON
_JYTHON_BASENAME=${JYTHON/:/-}
java -jar $VIRTUAL_ENV/javalib/${_JYTHON_BASENAME}.jar -s -d $VIRTUAL_ENV/jython
touch requirements.txt
BEFORE_PY_26=$($VIRTUAL_ENV/jython/bin/jython -c "import sys; print sys.version_info < (2, 6)")
if [ "$BEFORE_PY_26" == "True" ]
then
    # Travis CI virtualenv version is greater 1.9.1, which was the
    # last version compatible with Python version before 2.6
    pip install virtualenv==1.9.1
fi
virtualenv -p $VIRTUAL_ENV/jython/bin/jython ~/myvirtualenv
