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
