#!/bin/sh
set -e

[ -n "$JYTHON" ] && "${TRAVIS_BUILD_DIR}/ci/before_install_jython.sh" || "${TRAVIS_BUILD_DIR}/ci/before_install_nonjython.sh"

[ -n "$JYTHON" ] && cp requirements-jython.txt requirements.txt || cp requirements-python-${TRAVIS_PYTHON_VERSION}.txt requirements.txt

if [ -f requirements.txt ]
then
    pip install -r requirements.txt
fi
