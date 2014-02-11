#!/bin/bash
set -e

pip install jip==0.7
jip install org.python:$JYTHON
_JYTHON_BASENAME=${JYTHON/:/.}
java -jar $VIRTUAL_ENV/javalib/${_JYTHON_BASENAME}.jar -s -d $VIRTUAL_ENV/jython
touch requirements.txt
virtualenv -p $VIRTUAL_ENV/jython/bin/jython ~/myvirtualenv
