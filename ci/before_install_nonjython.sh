#!/bin/bash
set -e

if [ -f requirements-python-${TRAVIS_PYTHON_VERSION}.txt ]
then
    cat requirements-python-${TRAVIS_PYTHON_VERSION}.txt >> requirements.txt
fi
ln -s $VIRTUAL_ENV $HOME/myvirtualenv
