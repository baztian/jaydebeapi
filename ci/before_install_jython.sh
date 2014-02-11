#!/bin/bash
set -e

pip install jip==0.7
jip install org.python:$JYTHON
_JYTHON_BASENAME=${JYTHON/:/-}
OLD_VIRTUAL_ENV=$VIRTUAL_ENV
deactivate
java -jar $OLD_VIRTUAL_ENV/javalib/${_JYTHON_BASENAME}.jar -s -d ~/jython
touch requirements.txt
BEFORE_PY_26=$(~/jython/bin/jython -c "import sys; print sys.version_info < (2, 6)")
if [ "$BEFORE_PY_26" == "True" ]
then
    # Travis CI virtualenv version is greater 1.9.1, which was the
    # last version compatible with Python version before 2.6
    #curl https://raw.github.com/pypa/pip/master/contrib/get-pip.py -o get-pip.py
    #curl http://peak.telecommunity.com/dist/ez_setup.py -o ez_setup.py
    #$VIRTUAL_ENV/jython/bin/jython get-pip.py
    #$VIRTUAL_ENV/jython/bin/jython ez_setup.py
    #$VIRTUAL_ENV/jython/bin/easy_install install virtualenv==1.9.1
    #sudo pip install virtualenv==1.9.1
    sudo pip install virtualenv==1.7.1.2
fi
which virtualenv
virtualenv --version
virtualenv -p ~/jython/bin/jython ~/myvirtualenv
