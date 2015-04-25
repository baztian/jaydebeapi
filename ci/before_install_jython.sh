#!/bin/bash
set -e

JYTHON_JAR=$(./ci/mvnget.sh $JYTHON)
java -jar ${JYTHON_JAR} -s -d $HOME/jython

BEFORE_PY_26=$($HOME/jython/bin/jython -c "import sys; print sys.version_info < (2, 6)")
if [ "$BEFORE_PY_26" == "True" ]
then
    curl http://peak.telecommunity.com/dist/ez_setup.py -o ez_setup.py
    $HOME/jython/bin/jython ez_setup.py
    # Install the latest pip compatible with Jython 2.5.3
    $HOME/jython/bin/easy_install pip==1.2.1
else
    $HOME/jython/bin/jython -m ensurepip
fi

# Install the latest virtualenv compatible with Jython
$HOME/jython/bin/pip install virtualenv==1.9.1
$HOME/jython/bin/virtualenv $HOME/myvirtualenv

if [ "$BEFORE_PY_26" == "True" ]
then
    # No SSL support for Jython
    cat > $HOME/myvirtualenv/pip.conf <<EOF
[install]
insecure = true
EOF
    cat <<EOF >> $HOME/myvirtualenv/bin/activate
export PIP_CONFIG_FILE=$HOME/myvirtualenv/pip.conf
EOF
fi
