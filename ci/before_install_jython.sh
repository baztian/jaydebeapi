#!/bin/bash
set -e

pip install jip==0.7
jip install $JYTHON
NON_GROUP_ID=${JYTHON#*:}
_JYTHON_BASENAME=${NON_GROUP_ID/:/-}
OLD_VIRTUAL_ENV=$VIRTUAL_ENV
java -jar $OLD_VIRTUAL_ENV/javalib/${_JYTHON_BASENAME}.jar -s -d $HOME/jython

BEFORE_PY_26=$($HOME/jython/bin/jython -c "import sys; print sys.version_info < (2, 6)")
if [ "$BEFORE_PY_26" == "True" ]
then
    # Travis CI virtualenv version is greater 1.9.1, which was the
    # last version compatible with Python version before 2.6
    pip install virtualenv==1.9.1
    # No SSL support for Jython
    mkdir $HOME/.pip
    cat > $HOME/.pip/pip.conf <<EOF
[install]
insecure = true
EOF
fi
virtualenv --version
# --distribute is a workaround as setuptools don't install on Jython properly
virtualenv --distribute -p $HOME/jython/bin/jython $HOME/myvirtualenv
