#!/bin/bash
set -e

export BACKEND=hsqldb
#export JYTHON=org.python:jython-installer:2.5.3
export JYTHON=org.python:jython-installer:2.7.0
jip install $JYTHON
_JIP_HOME=$HOME/.jip
export HOME=`mktemp -d`
export TRAVIS_BUILD_DIR=$HOME/baztian/jaydebeapi

git clone "$(git rev-parse --show-toplevel)" $TRAVIS_BUILD_DIR
mkdir -p $TRAVIS_BUILD_DIR
cp -r "$(git rev-parse --show-toplevel)"/* $TRAVIS_BUILD_DIR

cd $TRAVIS_BUILD_DIR

mkdir -p $HOME/.jip/cache/org.python/
cp -r $_JIP_HOME/cache/org.python/jython-installer* $HOME/.jip/cache/org.python/

virtualenv $HOME/orig
source $HOME/orig/bin/activate
pip install --upgrade virtualenv

virtualenv $HOME/new
source $HOME/new/bin/activate

# required as new virtualenv doesn't have pip installed virtualenv
pip install --upgrade virtualenv

$TRAVIS_BUILD_DIR/ci/before_install_jython.sh

source $HOME/myvirtualenv/bin/activate

[ -x requirements.txt ] && pip install -r requirements.txt

pip install jip==0.7
pip install -e .
pip install -r test-requirements.txt
jip install org.xerial:sqlite-jdbc:3.7.2
jip install org.hsqldb:hsqldb:1.8.0.10

export CLASSPATH=$VIRTUAL_ENV/javalib/*
python test/testsuite.py test_integration.HsqldbTest

echo Remove ${HOME}?
read
rm -r $HOME
